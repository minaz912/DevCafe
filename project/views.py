from rest_framework.parsers import FileUploadParser
from project.serializers import ProjectSerializer, PostSerializer, \
    TaskSerializer, PostJobSerializer, \
    PostTaskSerializer, RequestSerializer , LogoSerializer , ContributorSerializer, ProjectSerializerForNoncontibutor,JobSerializer,ContribProjectSerializer
from project.models import Project, Post, Contributor, Task, Job, Request
from rest_framework import generics
from rest_framework.views import APIView
from project.permissions import IsOwnerOrReadOnly
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsOwnerOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(PM=self.request.user)

    def post(self, request):
        project = Project(title=request.data['title'],
                          description=request.data['description'],
                          plan=request.data.get('plan', ''), PM=request.user)
        project.save()
        serializer = ProjectSerializer(project,context={'request': request})
        Contributor.objects.create(
            user=self.request.user,
            project=project,
            is_pm=True)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (
        IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)

    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
            serializer = ProjectSerializer(project, context={'request': request})
            serializerForNonContributor = ProjectSerializerForNoncontibutor(project,context={'request': request})
            for contributor in project.contributors.all():
                if request.user == contributor.user:
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializerForNonContributor.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CreateJob(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        if request.user == project.PM:
            job = PostJobSerializer(data=request.data)
            if job.is_valid():
                job.save(project=project)
                return Response(job.data, status=status.HTTP_201_CREATED)
            return Response(job.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AssignTask(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, pk):
        #project = Project.objects.get(id=pk)
        contributor = Contributor.objects.get(id=pk)
        #if contributor.project == project:
        if request.user == contributor.project.PM:
            task = PostTaskSerializer(data=request.data)
            if task.is_valid():
                task.save(project=contributor.project, issued_to=contributor)
                tasks = Task.objects.filter(project=contributor.project)
                tasksser = TaskSerializer(tasks , many=True)
                return Response(tasksser.data, status=status.HTTP_201_CREATED)
            return Response(task.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
        #return Response(status=status.HTTP_404_NOT_FOUND)


class ApplyForJob(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, pk):
        try:
            job = Job.objects.get(id=pk)
            job_request = Request.objects.filter(owner=request.user, job=job)
            if job.project.PM == request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if job_request.exists():
                if job.is_taken:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_200_OK)
            new_req = Request(owner=request.user, job=job)
            new_req.save()
            serializer = RequestSerializer(new_req,context={'request': request})
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ViewRequests(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        try:
            project = Project.objects.get(id=pk)
            if project.PM == request.user:
                req = Request.objects.filter(job__project=project)
                serializer = RequestSerializer(req, many=True ,context={'request': request})
                return Response(serializer.data)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception, e:
            raise e


class ResolveRequests(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, pk, ans):
        try:
            req = Request.objects.get(pk=pk)
            if ans == '1':
                job = req.job
                if not job.is_taken:
                    job.is_taken = True
                    job.issued_to = req.owner
                    job.save()
                    contr = Contributor(job=job, user=req.owner, project=job.project, is_pm=False)
                    # Contributor.objects.create(job=job, user=req.owner, project=job.project, is_pm=False)
                    contr.save()
                    serializer = ContributorSerializer(contr)
                    req.delete()
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # job is already taken
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            elif ans == '0':
                req.delete()
                return Response(status=status.HTTP_200_OK)

        except Exception, e:
            # return Response(status=status.HTTP_404_NOT_FOUND)
            raise e


class ViewMyTasks(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        try:
            project = Project.objects.get(id=pk)
            if request.user == project.PM:
                task = Task.objects.filter(project=project)
            else:
                contributor = Contributor.objects.get(user=request.user,
                                                  project=project)
                task = Task.objects.filter(project=project, issued_to=contributor)
            serializer = TaskSerializer(task, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Contributor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class MakeTaskDone(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self , request , pk):
        try:
            task = Task.objects.get(id=pk)
            proj = Project.objects.get(id=task.project_id)
            if request.user == proj.PM or request.user == task.issued_to.user:
                task.is_done=not task.is_done
                task.save()
                serializer = TaskSerializer(task)
                return Response(data=serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Task.DoesNotExist or Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UploadProjectLogo(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    parser_classes = (FileUploadParser,)

    def post(self , request):
        if not request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        logo = request.FILES['file']
        id = request.DATA['projid']
        if logo:
            try:
                proj = Project.objects.get(id=id)
                proj.logo = logo
                proj.save()
                serializer = LogoSerializer(proj)
            except proj.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(data=serializer.data , status=status.HTTP_200_OK)


class Quit(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, pk):
        try:
            project = Project.objects.get(id=pk)
            contributor = Contributor.objects.get(user=request.user, project=project)
            if project.PM == request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            contributor.delete()
            project.save()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ViewJobs(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self , request):
        try:
            jobs = Job.objects.filter(is_taken=False).order_by('-time_posted')
            serliaizer = JobSerializer(jobs , many=True ,context={'request': request})
            return Response(data=serliaizer.data,status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ViewMyProjects(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self , request):
        try:
            myprojs = Contributor.objects.filter(user=request.user)
            serializer = ContribProjectSerializer(myprojs , many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        except Contributor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)