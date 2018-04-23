from pyroutelib3 import Router

router = Router("car", "bayern.osm")


def main_router(self):
    start_lat = 48.085468
    start_lon = 11.276009
    end_lat   = 48.138384
    end_lon   = 11.520802

    start = router.data.findNode(start_lat, start_lon)
    end = router.data.findNode(end_lat, end_lon)

    status, route = router.doRoute(start, end)

    if status == 'success':
        routeLatLons = list(map(router.nodeLatLon,route))
        print(routeLatLons)


if __name__ == '__main__':
    ex = main_router()
    sys.exit(app.exec_())
