from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
import json
from graph_stuff import choose_apartments, short_path_tree, matrix_for_cluster, cluster2, cluster3, cluster5, coordinates_and_matrix, find_nearest_hospitals_1a, tuda, suda, tuda_suda, find_in_radius_1b, tuda_radius, suda_radius, tuda_suda_radius, get_optimal_hospitals_2, min_sum_hosp_3, short_tree_4, find_the_distance, nodes_in_radius

app = Flask(__name__)
CORS(app)
api = Api(app)


class SomeFunc(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        # data["fullName"]
        if not 1:
            response = app.response_class(
                response=jsonify({"message": "Couldn't do something"}),
                status=500,
                mimetype="application/json",
            )
            return response

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "Everything went fine!",
                    "nodes": [[55.782440, 49.155101], [55.796860, 49.126115]],
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response


class GenerateNodes(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        N = data["numberOfNodes"]
        # if not choose_apartments(N):
        #     response = app.response_class(
        #         response=jsonify({"message": "Неизвестная ошибка"}),
        #         status=500,
        #         mimetype="application/json",
        #     )
        #     return response
        nodes = choose_apartments(int(N))

        response = app.response_class(
            response=json.dumps({"message": "генерация узлов прошла успешно!", "nodes": nodes}),
            status=201,
            mimetype="application/json",
        )
        return response


class GenerateShortPathTree(Resource):
    def post(self):
        nodes, treeWeight, pathLength = short_path_tree()
        response = app.response_class(
            response=json.dumps(
                {
                    "message": "генерация дерева кратчайших путей прошла успешно!",
                    "nodes": nodes,
                    "treeWeight": treeWeight,
                    "pathLength": pathLength,
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class GenerateClusterization(Resource):
    def post(self):
        matrix_for_cluster()
        response = app.response_class(
            response=json.dumps(
                {
                    "message": "кластеризация прошла успешно!",
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response


class GenerateClusterTrees(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        N = data["numberOfClusters"]
        if N == 2:
            hospCoords, centroidsCoords, nodes, treeWeight, pathLength = cluster2()
        elif N == 3:
            hospCoords, centroidsCoords, nodes, treeWeight, pathLength = cluster3()
        else:
            hospCoords, centroidsCoords, nodes, treeWeight, pathLength = cluster5()

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "генерация кластеров прошла успешно!",
                    "nodes": nodes,
                    "hospCoords": hospCoords,
                    "centroidsCoords": centroidsCoords,
                    "treeWeight": treeWeight,
                    "pathLength": pathLength,
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FirstTaskGenerateNodes(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        N1 = data["numberOfHosps"]
        N2 = data["numberOfHomes"]
        hospsHomes = coordinates_and_matrix(int(N1), int(N2))
        response = app.response_class(
            response=json.dumps(
                {
                    "message": "генерация домов и больниц прошла успешно!",
                    "hospNodes": hospsHomes[0],
                    "homeNodes": hospsHomes[1],
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindNearObjects(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        N2 = data["numberOfHomes"]
        find_nearest_hospitals_1a(int(N2))
        response = app.response_class(
            response=json.dumps(
                {
                    "message": "ближайшие объекты были найдены успешно!",
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindRoute(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        aptCoordinates = data["aptCoords"]
        direction = data["direction"]
        route = []
        if direction == "tuda":
            route = tuda(aptCoordinates)
        elif direction == "suda":
            route = suda(aptCoordinates)
        else:
            route = tuda_suda(aptCoordinates)

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "маршрут успешно найден!",
                    "route": route
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindNearObjectsUsingRadius(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        N2 = data["numberOfHomes"]
        r = data["radiusOfSearch"]
        find_in_radius_1b(int(r), int(N2))

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "ближайшие объекты в заданном пределе расстояния успешно найдены!",
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindRoutes(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        aptCoordinates = data["aptCoords"]
        direction = data["direction"]
        routes = []
        if direction == "tuda":
            routes = tuda_radius(aptCoordinates)
        elif direction == "suda":
            routes = suda_radius(aptCoordinates)
        else:
            routes = tuda_suda_radius(aptCoordinates)

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "маршруты в заданном пределе расстояния успешно найдены!",
                    "routes": routes
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindOptimalHospitals(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        num = data["numberOfHomes"]
        hospsCoords = get_optimal_hospitals_2(int(num))

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "координаты больниц успешно найдены!",
                    "hospsCoords": hospsCoords
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindMinSumHospital(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        num = data["numberOfHomes"]
        hospCoord = min_sum_hosp_3(int(num))

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "координаты больницы успешно найдены!",
                    "hospCoord": hospCoord
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindShortTreeHosp(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        num = data["numberOfHomes"]
        hospCoord = short_tree_4(int(num))

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "координаты больницы успешно найдены!",
                    "hospCoord": hospCoord
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindRadiusDistances(Resource):
    def post(self):
        find_the_distance()
        response = app.response_class(
            response=json.dumps(
                {
                    "message": "успешно посчитано!",
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

class FindObjectsWithinRadius(Resource):
    def post(self):
        data = json.loads(request.form["filter"])
        aptCoords = data["aptCoords"]
        r = data["rds"]
        nearNodes = nodes_in_radius(int(r), aptCoords)

        response = app.response_class(
            response=json.dumps(
                {
                    "message": "ближайшие объекты в заданном радиусе успешно найдены!",
                    "nearNodes": nearNodes
                }
            ),
            status=201,
            mimetype="application/json",
        )
        return response

api.add_resource(SomeFunc, "/some-func")
api.add_resource(GenerateNodes, "/generate-nodes")
api.add_resource(GenerateShortPathTree, "/generate-short-path-tree")
api.add_resource(GenerateClusterization, "/generate-clusterization")
api.add_resource(GenerateClusterTrees, "/generate-cluster-trees")

api.add_resource(FirstTaskGenerateNodes, "/first-task-generate-nodes")
api.add_resource(FindNearObjects, "/find-near-objects")
api.add_resource(FindRoute, "/find-route")
api.add_resource(FindNearObjectsUsingRadius, "/find-routes-with-radius")
api.add_resource(FindRoutes, "/find-radius-routes")
api.add_resource(FindOptimalHospitals, "/find-optimal-hospitals")
api.add_resource(FindMinSumHospital, "/find-min-sum-hospital")
api.add_resource(FindShortTreeHosp, "/find-short-tree-hospital")
api.add_resource(FindRadiusDistances, "/find-radius-distances")
api.add_resource(FindObjectsWithinRadius, "/find-objects-within-radius")

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=80, debug=False)
    # app.run(host="127.0.0.1", port=82, debug=False)
    app.run(port=5000, debug=True)
