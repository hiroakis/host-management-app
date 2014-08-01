var api = 'http://localhost:8080';

angular.module('app', ['ngRoute', 'xeditable', 'ui.bootstrap'])
    .config(function($routeProvider){
        $routeProvider
            .when('/ip', {
                templateUrl: 'partials/ip.html',
                controller: 'IPController'
            })
            .when('/role', {
                templateUrl: 'partials/role.html',
                controller: 'RoleController'
            })
            .when('/host', {
                templateUrl: 'partials/host.html',
                controller: 'HostController'
            })
            .otherwise({
                redirectTo: '/host'
            });

    }).controller('IPController', function($scope, AppService, DialogService){
 
        var url = api + '/api/ip';
 
        $scope.ipaddrs = [];
 
        // get all
        AppService.get(url).success(function(res){
            for(var i = 0; i < res.result.length; i++){
                if(res.result[i].is_used == 0){
                    res.result[i].is_used = "No";
                } else {
                    res.result[i].is_used = "Yes";
                }
            }
            $scope.ipaddrs = res.result;
        }).error(function(data, status, headers, config){
            var message = 'Could not get data from api. HTTP status: ' + status;
            DialogService.showErrorDialog($scope, message);
        });
 
        // add
        $scope.add = function(){
            $scope.inserted = {
                ip: '',
                is_used: 0,
            };
            $scope.ipaddrs.push($scope.inserted);
        };
     
        // update
        $scope.save = function(index, ipaddr, dataPosted){
           AppService.save(url, ipaddr, dataPosted).success(function(){

           }).error(function(data, status, headers, config){
                if (config.method == 'POST') {
                   $scope.ipaddrs.pop($scope.inserted);
                   var message = 'Could not add';
                   DialogService.showErrorDialog($scope, message);
                } else if(config.method == 'PUT') {
                   $scope.ipaddrs[index].ip = ipaddr;
                   var message = 'Could not update';
                   DialogService.showErrorDialog($scope, message);
                }
                
           });
        };
     
        // confirm
        $scope.confirmDelete = function(index){
            DialogService.showDeleteDialog($scope, index, $scope.ipaddrs[index].ip);
        };

        // remove
        $scope.remove = function(index){
            AppService.remove(url, $scope.ipaddrs[index].ip).success(function(){
                $scope.ipaddrs.splice(index, 1);
            }).error(function(data){
                var message = 'Could not delete ip: ' + $scope.ipaddrs[index].ip + '. It is used.';
                DialogService.showErrorDialog($scope, message);
            });
        };
 
     }).controller('RoleController', function($scope, AppService, DialogService){

        var url = api + '/api/role';
 
        $scope.roles = [];
 
        // get all
        AppService.get(url).success(function(res){
            $scope.roles = res.result;
        }).error(function(data, status, headers, config){
            var message = 'Could not get data from api. HTTP status: ' + status;
            DialogService.showErrorDialog($scope, message);
        });
 
        // add
        $scope.add = function(){
            $scope.inserted = {
                role: ''
            };
            $scope.roles.push($scope.inserted);
        };
     
        // update
        $scope.save = function(index, role, dataPosted){
           AppService.save(url, role, dataPosted).success(function(){

           }).error(function(data, status, headers, config){
                if (config.method == 'POST') {
                   $scope.roles.pop($scope.inserted);
                   var message = 'Could not add';
                   DialogService.showErrorDialog($scope, message);
                } else if(config.method == 'PUT') {
                   $scope.roles[index].role = role;
                   var message = 'Could not update';
                   DialogService.showErrorDialog($scope, message);
                }
                
           });
        };
     
        // confirm
        $scope.confirmDelete = function(index){
            DialogService.showDeleteDialog($scope, index, $scope.roles[index].role);
        };

        // remove
        $scope.remove = function(index){
            AppService.remove(url, $scope.roles[index].role).success(function(){
                $scope.roles.splice(index, 1);
            }).error(function(data){
                var message = 'Could not delete role: ' + $scope.roles[index].role + '. It may be used.';
                DialogService.showErrorDialog($scope, message);
            });
        };
 
    }).controller('HostController', function($scope, AppService, DialogService){

        var url = api + '/api/host'

        $scope.hosts = [];
        $scope.ipaddrs = [];
        $scope.roles = [];

        // get all
        AppService.get(url).success(function(res){
            $scope.hosts = res.result;
        }).error(function(data, status, headers, config){
            var message = 'Could not get data from api. HTTP status: ' + status;
            DialogService.showErrorDialog($scope, message);
        });
 
        // add
        $scope.add = function(){
            $scope.inserted = {
                host_name: '',
                ip: '',
                role: [],
            };
            $scope.hosts.push($scope.inserted);
        };
     
        // update
        $scope.save = function(index, targetHost, dataPosted){
           AppService.save(url, targetHost, dataPosted).success(function(){

           }).error(function(data, status, headers, config){
                if (config.method == 'POST') {
                    $scope.hosts.pop($scope.inserted);
                    var message = 'Could not add';
                    DialogService.showErrorDialog($scope, message);
                } else if(config.method == 'PUT') {
                    $scope.hosts[index].host_name = targetHost;
                    var message = 'Could not update';
                    DialogService.showErrorDialog($scope, message);
                }
           });
        };

        // confirm
        $scope.confirmDelete = function(index){
            DialogService.showDeleteDialog($scope, index, $scope.hosts[index].host_name);
        };
     
        // remove
        $scope.remove = function(index){

            AppService.remove(url, $scope.hosts[index].host_name).success(function(){
                $scope.hosts.splice(index, 1);
            }).error(function(data){
                var message = 'Could not delete host: ' + $scope.hosts[index].host_name;
                DialogService.showErrorDialog($scope, message);
            });
        };

        $scope.loadAvailableIP = function(){
            AppService.get(api + '/api/list/ip/unused').success(function(res){
                $scope.ipaddrs = res.result;
            });
        };
    
        $scope.loadRole = function(){
            AppService.get(api + '/api/list/role').success(function(json){
                $scope.roles = json.result;
            });
        };

    }).factory('AppService', function($http){
 
        var appService = {
            get: function(url){
                return $http.get(url);
            }, 
            save: function(url, updateTarget, dataPosted){
                if (updateTarget == ''){
                    return $http.post(url, dataPosted);
                } else {
                    return $http.put(url + '/' + updateTarget, dataPosted);
                }
            },
            remove: function(url, deleteTarget){
                return $http.delete(url + '/' + deleteTarget);
            }
        };

        return appService;
 
    }).factory('DialogService', function($modal){
        var dialogService = {
            showDeleteDialog: function(scope, index, message){
                scope.index = index;
                scope.message = message;
                $modal.open({templateUrl: "modal/delete.html", scope: scope});
            },
            showErrorDialog: function(scope, message){
                scope.message = message;
                $modal.open({templateUrl: "modal/error.html", scope: scope});
            }
        };

        return dialogService;
    });

