/**
* LandingPageController
* @namespace devcafe.layout.controllers
*/
(function () {
    'use strict';

    angular
        .module('devcafe.layout.controllers')
        .controller('LandingPageController', LandingPageController);

        LandingPageController.$inject = ['$scope', '$rootScope', 'Userapp'];

    /**
    * @namespace NavbarController
    */
    function LandingPageController($scope, $rootScope, Userapp) {
        var vm = this;

        // vm.logout = logout;

        // $scope.$watch('search', function() {
        //     $rootScope.searchQuery = $scope.search;
        // });

        // $rootScope.$on("$locationChangeStart", function(event, next, current) { 
        //     $('.searchInput').val('');
        //     $rootScope.searchQuery = "";
        // });

        // /**
        // * @name logout
        // * @desc Log the user out
        // * @memberOf devcafe.layout.controllers.NavbarController
        // */
        // function logout() {
        //     Userapp.logout();
        // }
    }
})();
