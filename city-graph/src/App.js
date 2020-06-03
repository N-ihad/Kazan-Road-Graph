import React, { useState, useCallback, useRef, useEffect } from "react";
import "./App.css";
import {
  Map,
  Marker,
  Popup,
  TileLayer,
  Circle,
  Tooltip,
  Polyline,
} from "react-leaflet";
import "pretty-checkbox";
import { Checkbox, Switch, Radio } from "pretty-checkbox-react";
import { map, tileLayer, marker, Routing, latLng } from "leaflet";
import AntPath from "react-leaflet-ant-path";
import axios from "axios";
import { Input } from "react-nice-inputs";
import NumPad from "react-numpad";
import {
  Form,
  Button,
  Alert,
  Badge,
  Container,
  Row,
  Col,
} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css";
import RingLoader from "react-spinners/RingLoader";
import Poppup from "./components/Poppup";
import { HospitalIcon, HomeIcon, ClusterIcon } from "./components/NodeIcon";

const styles = {
  generateButton: {
    marginTop: "15px",
    width: "100%",
  },
  loading: {
    transform: "translate(-50%, -50%)",
    left: "63%",
    top: "50%",
    filter: "brightness(100%) !important",
    zIndex: "10000",
    position: "absolute",
  },
  sendData: {
    marginTop: "15px",
  },
  clearButton: {
    marginTop: "15px",
  },
};

const initialMapDisplayFilterState = {
  nodes: false,
  shortPathTree: false,
  clusterization: false,
  homesAndHosps: false,
  currentRoute: false,
  currentRadiusRoute: false,
  optimalHospitals: false,
  minSumHospital: false,
  shortTreeHospital: false,
  radiusCircle: false,
};

const endpoints = {
  generateNodes: "http://127.0.0.1:5000/generate-nodes",
  generateShortPathTree: "http://127.0.0.1:5000/generate-short-path-tree",
  generateCluserization: "http://127.0.0.1:5000/generate-clusterization",
  generateClusterTrees: "http://127.0.0.1:5000/generate-cluster-trees",
  firstTaskGenerateNodes: "http://127.0.0.1:5000/first-task-generate-nodes",
  findNearObjects: "http://127.0.0.1:5000/find-near-objects",
  findRoute: "http://127.0.0.1:5000/find-route",
  findNearObjectsUsingRadius: "http://127.0.0.1:5000/find-routes-with-radius",
  findRoutes: "http://127.0.0.1:5000/find-radius-routes",
  findOptimalHospitals: "http://127.0.0.1:5000/find-optimal-hospitals",
  findMinSumHospital: "http://127.0.0.1:5000/find-min-sum-hospital",
  findShortTreeHospital: "http://127.0.0.1:5000/find-short-tree-hospital",
  findRadiusDistances: "http://127.0.0.1:5000/find-radius-distances",
  findNearObjectsWithinRadius: "http://127.0.0.1:5000/find-objects-within-radius",
};

const initialClusterTogglesState = {
  two: false,
  three: false,
  five: false,
};

const initialDirectionTogglesState = {
  tuda: false,
  suda: false,
  tudaSuda: false,
};

const initialClusterInfoState = {
  cluster2: {
    treeWeight: "",
    pathLength: "",
  },
  cluster3: {
    treeWeight: "",
    pathLength: "",
  },
  cluster5: {
    treeWeight: "",
    pathLength: "",
  },
};

const App = () => {
  const kazanCenterPosition = [55.7879, 49.1233];
  const [checked, setChecked] = useState(false);
  const [mapDisplayFilter, setMapDisplayFilter] = useState({
    ...initialMapDisplayFilterState,
  });
  const [initialDataIsPrepared, setInitialDataIsPrepared] = useState(false);
  const [listOfNodes, setListOfNodes] = useState([]);
  const [shortPathTreeNodes, setShortPathTreeNodes] = useState([]);
  const [shortPathTreeInfo, setShortPathTreeInfo] = useState({
    treeWeight: "",
    pathLength: "",
  });
  const [numberOfNodes, setNumberOfNodes] = useState(0);
  const [loading, setLoading] = useState(false);
  const [alrt, setAlrt] = useState({
    show: false,
    variant: "success",
    message: "Все прошло успешно!",
  });
  const [numberOfClusters, setNumberOfClusters] = useState();
  const [clusterToggles, setClusterToggles] = useState({
    ...initialClusterTogglesState,
  });
  const [isClusterized, setIsClusterized] = useState(false);
  const [listOfTrees, setListOfTrees] = useState([]);
  const [clusterInfo, setClusterInfo] = useState({
    ...initialClusterInfoState,
  });
  const [clusterNodes, setClusterNodes] = useState([]);

  const [homeNodes, setHomeNodes] = useState([]);
  const [hospNodes, setHospNodes] = useState([]);
  const [numberOfHomes, setNumberOfHomes] = useState(0);
  const [numberOfHosps, setNumberOfHosps] = useState(0);

  const [currentRoute, setCurrentRoute] = useState([[]]);
  const [directionName, setDirectionName] = useState("");
  const [selectedHomeCoords, setSelectedHomeCoords] = useState([]);
  const [firstTaskDataIsPrepared, setFirstTaskDataIsPrepared] = useState(false);
  const [radiusOfSearch, setRadiusOfSearch] = useState();
  const [isRadiusExists, setIsRadiusExists] = useState(false);
  const [listOfRoutes, setListOfRoutes] = useState([[]]);
  const [firstTaskDataIsPrepared1, setFirstTaskDataIsPrepared1] = useState(
    false
  );
  const [optimalHospitals, setOptimalHospitals] = useState([]);
  const [minSumHospital, setMinSumHospital] = useState();
  const [shortTreeHospital, setShortTreeHosp] = useState();
  const [routesWithinRadius, setRoutesWithinRadius] = useState([]);
  const [realRadius, setRealRadius] = useState();
  const [isRealRadiusExists, setIsRealRadiusExists] = useState(false);
  // const isFirstRun = useRef(true);

  const successAlrt = (serverMsg) => {
    setAlrt(
      {
        show: true,
        variant: "success",
        message: "Все прошло успешно! Сообщение от сервера >>> " + serverMsg,
      },
      window.setTimeout(() => {
        setAlrt({ ...alrt, show: false });
      }, 2000)
    );
  };

  const failAlrt = (serverMsg) => {
    setAlrt(
      {
        show: true,
        variant: "danger",
        message:
          "Произошла неизвестная ошибка! Сообщение от сервера >>> " + serverMsg,
      },
      window.setTimeout(() => {
        setAlrt({ ...alrt, show: false });
      }, 2000)
    );
  };

  const handleNumberOfNodes = (value) => {
    setNumberOfNodes(value);
  };

  const handleNumberOfHomes = (value) => {
    setNumberOfHomes(value);
  };

  const handleNumberOfHosps = (value) => {
    setNumberOfHosps(value);
  };

  const handleGenerateNumberOfNodes = () => {
    clearAll();
    setLoading(true);
    const options = {
      numberOfNodes: numberOfNodes,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.generateNodes, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setListOfNodes(response.data.nodes);
        setInitialDataIsPrepared(true);
        setMapDisplayFilter({
          ...mapDisplayFilter,
          nodes: true,
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const handleGenerateShortPathTree = () => {
    setLoading(true);
    let data = new FormData();
    axios
      .post(endpoints.generateShortPathTree, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setShortPathTreeNodes(response.data.nodes);
        setShortPathTreeInfo({
          treeWeight: response.data.treeWeight,
          pathLength: response.data.pathLength,
        });
        setMapDisplayFilter({
          ...mapDisplayFilter,
          shortPathTree: true,
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const clearAll = () => {
    setShortPathTreeNodes([]);
    setListOfNodes([]);
    setShortPathTreeInfo({
      treeWeight: "",
      pathLength: "",
    });
    setClusterInfo({
      ...initialClusterInfoState,
    });
    setInitialDataIsPrepared(false);
    setIsClusterized(false);
    setClusterToggles({
      ...initialClusterTogglesState,
    });
    setMapDisplayFilter({
      ...initialMapDisplayFilterState,
    });
    setClusterNodes([]);
  };

  const handleCheckBoxClusterChange = (num) => {
    let clstName = "";
    if (num === 2) {
      setClusterToggles({
        ...initialClusterTogglesState,
        two: true,
      });
      clstName = "cluster2";
      setNumberOfClusters(num);
    } else if (num === 3) {
      setClusterToggles({
        ...initialClusterTogglesState,
        three: true,
      });
      clstName = "cluster3";
      setNumberOfClusters(num);
    } else {
      setClusterToggles({
        ...initialClusterTogglesState,
        five: true,
      });
      clstName = "cluster5";
      setNumberOfClusters(num);
    }
    setLoading(true);
    const options = {
      numberOfClusters: num,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.generateClusterTrees, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          nodes: true,
          clusterization: true,
        });
        setListOfTrees(response.data.nodes);
        setClusterNodes(response.data.centroidsCoords);
        setClusterInfo({
          ...clusterInfo,
          [clstName]: {
            treeWeight: response.data.treeWeight,
            pathLength: response.data.pathLength,
          },
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const handleClusterization = () => {
    setLoading(true);
    let data = new FormData();
    axios
      .post(endpoints.generateCluserization, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        setIsClusterized(true);
        successAlrt(response.data.message);
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const colorForCluster = (clusterID) => {
    switch (clusterID) {
      case 1:
        return "cyan";
      case 2:
        return "blue";
      case 3:
        return "#ff00fb";
      case 4:
        return "violet";
      case 5:
        return "black";
      default:
        break;
    }
  };

  const handleDirectionCheckboxChange = (name) => {
    setDirectionName(name);
  };

  const handleGenerateHomesHosps = () => {
    setLoading(true);
    const options = {
      numberOfHomes: numberOfHomes,
      numberOfHosps: numberOfHosps,
    };
    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.firstTaskGenerateNodes, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        setHomeNodes(response.data.homeNodes);
        setHospNodes(response.data.hospNodes);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
        });
        setFirstTaskDataIsPrepared(true);
        successAlrt(response.data.message);
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const handleNearObjectsGeneration = () => {
    setLoading(true);
    const options = {
      numberOfHomes: numberOfHomes,
    };
    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findNearObjects, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        setFirstTaskDataIsPrepared(true);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          currentRoute: true,
        });
        successAlrt(response.data.message);
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const handleNearObjectsGenerationUsingRadius = () => {
    setLoading(true);
    const options = {
      numberOfHomes: numberOfHomes,
      radiusOfSearch: radiusOfSearch,
    };
    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findNearObjectsUsingRadius, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        setFirstTaskDataIsPrepared1(true);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          currentRadiusRoute: true,
        });
        successAlrt(response.data.message);
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const handleClickRadius = (coords) => {
    setLoading(true);
    const options = {
      aptCoords: coords,
      direction: directionName,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findRoutes, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setListOfRoutes(response.data.routes);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          currentRadiusRoute: true,
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const handleClick = (coords) => {
    setSelectedHomeCoords(coords);
    if (isRealRadiusExists) {
      findObjectsWithinRadius();
    }
    if (isRadiusExists) {
      handleClickRadius(coords);
    } else {
      setLoading(true);
      const options = {
        aptCoords: coords,
        direction: directionName,
      };

      let data = new FormData();
      data.append("filter", JSON.stringify({ ...options }));
      axios
        .post(endpoints.findRoute, data, {
          headers: {
            accept: "application/json",
            "Accept-Language": "en-US,en;q=0.8",
            "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
          },
        })
        .then((response) => {
          setLoading(false);
          successAlrt(response.data.message);
          setCurrentRoute(response.data.route);
          setMapDisplayFilter({
            ...initialMapDisplayFilterState,
            homesAndHosps: true,
            currentRoute: true,
          });
        })
        .catch((error) => {
          setLoading(false);
          failAlrt(error);
        });
    }
  };

  const generateOptimalHospitals = () => {
    setLoading(true);
    const options = {
      numberOfHomes: numberOfHomes,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findOptimalHospitals, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setOptimalHospitals(response.data.hospsCoords);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          optimalHospitals: true,
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const generateMinSumHospital = () => {
    setLoading(true);
    const options = {
      numberOfHomes: numberOfHomes,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findMinSumHospital, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setMinSumHospital(response.data.hospCoord);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          minSumHospital: true,
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const generateShortTreeHospital = () => {
    setLoading(true);
    const options = {
      numberOfHomes: numberOfHomes,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findShortTreeHospital, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setShortTreeHosp(response.data.hospCoord);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          shortTreeHospital: true,
        });
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const findRadiusDistances = () => {
    setLoading(true);
    let data = new FormData();
    axios
      .post(endpoints.findRadiusDistances, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setMapDisplayFilter({
          ...initialMapDisplayFilterState,
          homesAndHosps: true,
          radiusCircle: true,
        });
        setDirectionName('');
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const findObjectsWithinRadius = () => {
    setLoading(true);
    const options = {
      aptCoords: selectedHomeCoords,
      rds: realRadius,
    };

    let data = new FormData();
    data.append("filter", JSON.stringify({ ...options }));
    axios
      .post(endpoints.findNearObjectsWithinRadius, data, {
        headers: {
          accept: "application/json",
          "Accept-Language": "en-US,en;q=0.8",
          "Content-Type": `multipart/form-data; boundary=${data._boundary}`,
        },
      })
      .then((response) => {
        setLoading(false);
        successAlrt(response.data.message);
        setRoutesWithinRadius(response.data.nearNodes);
      })
      .catch((error) => {
        setLoading(false);
        failAlrt(error);
      });
  };

  const retDescription = (key) => {
    switch (key) {
      case 0:
        return "туда";
      case 1:
        return "сюда";
      case 2:
        return "туда-сюда";
      default:
        break;
    }
  };

  const retColor = (key) => {
    switch (key) {
      case 0:
        return "red";
      case 1:
        return "blue";
      case 2:
        return "green";
      default:
        break;
    }
  };

  return (
    <div className="App">
      {alrt.show && (
        <Alert
          variant={alrt.variant}
          style={{
            position: "absolute",
            zIndex: "10000",
            width: "95%",
            left: "0",
            right: "0",
            marginLeft: "auto",
            marginRight: "auto",
          }}
          onClose={() => setAlrt({ ...alrt, show: false })}
          dismissible
        >
          {alrt.message}
        </Alert>
      )}
      <div className="Main">
        <div className="filters-window">
          <h4 style={{ marginBottom: "15px" }}>
            <Badge pill variant="light">
              Первая часть
            </Badge>{" "}
          </h4>
          <NumPad.Number
            onChange={(value) => {
              handleNumberOfNodes(value);
            }}
            value={numberOfNodes}
            label={"Количество узлов"}
            placeholder={"0"}
            negative={false}
            decimal={0}
          >
            <input className="input-number-of-nodes" />
          </NumPad.Number>
          <Button
            style={styles.generateButton}
            variant="secondary"
            onClick={handleGenerateNumberOfNodes}
            disabled={numberOfNodes === 0 ? true : false}
          >
            Сгенерировать на карте
          </Button>
          <Button
            style={styles.generateButton}
            variant="secondary"
            onClick={handleGenerateShortPathTree}
            disabled={!initialDataIsPrepared ? true : false}
          >
            Дерево кратчайших путей
          </Button>
          <div style={{ marginTop: "15px" }}>
            <Form.Check
              inline
              label="2"
              checked={clusterToggles.two}
              onChange={() => handleCheckBoxClusterChange(2)}
              disabled={!isClusterized}
            />
            <Form.Check
              inline
              label="3"
              checked={clusterToggles.three}
              onChange={() => handleCheckBoxClusterChange(3)}
              disabled={!isClusterized}
            />
            <Form.Check
              inline
              label="5"
              checked={clusterToggles.five}
              onChange={() => handleCheckBoxClusterChange(5)}
              disabled={!isClusterized}
            />
          </div>
          <Button
            style={styles.generateButton}
            variant={
              isClusterized && initialDataIsPrepared ? "success" : "secondary"
            }
            onClick={handleClusterization}
            disabled={!isClusterized && initialDataIsPrepared ? false : true}
          >
            {isClusterized ? "Кластеризован" : "Кластеризовать"}
          </Button>
          <Poppup infoToShow={shortPathTreeInfo} clusterInfo={clusterInfo} />
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          <br />
          <h4 style={{ marginBottom: "15px", marginTop: "20px" }}>
            <Badge pill variant="light">
              Вторая часть
            </Badge>{" "}
          </h4>
          <Container style={{ padding: "0" }}>
            <span>Количество домов и больниц</span>
            <Row style={{ marginTop: "10px" }}>
              <Col>
                <NumPad.Number
                  onChange={(value) => {
                    handleNumberOfHomes(value);
                  }}
                  value={numberOfHomes}
                  placeholder={"0"}
                  negative={false}
                  decimal={0}
                >
                  <input className="input-number-of-nodes" />
                </NumPad.Number>
              </Col>
              <Col>
                <NumPad.Number
                  onChange={(value) => {
                    handleNumberOfHosps(value);
                  }}
                  value={numberOfHosps}
                  placeholder={"0"}
                  negative={false}
                  decimal={0}
                >
                  <input className="input-number-of-nodes" />
                </NumPad.Number>
              </Col>
            </Row>
            <Button
              style={styles.generateButton}
              variant="secondary"
              onClick={handleGenerateHomesHosps}
              disabled={
                numberOfHomes === 0 || numberOfHosps === 0 ? true : false
              }
            >
              Сгенерировать на карте
            </Button>
            <Button
              style={styles.generateButton}
              variant="secondary"
              onClick={handleNearObjectsGeneration}
              disabled={!firstTaskDataIsPrepared}
            >
              Найти ближайшие объекты
            </Button>
            <div style={{ marginTop: "15px" }}>
              <Form.Check
                inline
                label="Туда"
                checked={directionName === "tuda" ? true : false}
                onChange={() => handleDirectionCheckboxChange("tuda")}
              />
              <Form.Check
                inline
                label="Обратно"
                checked={directionName === "suda" ? true : false}
                onChange={() => handleDirectionCheckboxChange("suda")}
              />
              <Form.Check
                inline
                label="Туда-обратно"
                checked={directionName === "tuda-suda" ? true : false}
                onChange={() => handleDirectionCheckboxChange("tuda-suda")}
              />
              <NumPad.Number
                onChange={(value) => {
                  setRadiusOfSearch(value);
                }}
                value={radiusOfSearch}
                placeholder={"0"}
                negative={false}
                decimal={0}
              >
                <input className="input-number-of-nodes" />
              </NumPad.Number>
              <Form.Check
                inline
                label="В пределах расстояния"
                checked={isRadiusExists}
                onChange={() => setIsRadiusExists(!isRadiusExists)}
              />
              <Button
                style={styles.generateButton}
                variant="secondary"
                onClick={handleNearObjectsGenerationUsingRadius}
                disabled={!firstTaskDataIsPrepared}
              >
                Найти ближайшие объекты не далее чем в Х метрах
              </Button>
              <Button
                style={styles.generateButton}
                variant="secondary"
                onClick={generateOptimalHospitals}
                disabled={!firstTaskDataIsPrepared}
              >
                Найти больницы с минимальным расстоянием до самого дальнего дома
              </Button>
              <Button
                style={styles.generateButton}
                variant="secondary"
                onClick={generateMinSumHospital}
                disabled={!firstTaskDataIsPrepared}
              >
                Найти больницу с минимальной суммой длин кратчайших путей
              </Button>
              <Button
                style={styles.generateButton}
                variant="secondary"
                onClick={generateShortTreeHospital}
                disabled={!firstTaskDataIsPrepared}
              >
                Найти больницу с минимальным весом дерева кратчайших путей
              </Button>
              <NumPad.Number
                onChange={(value) => {
                  setRealRadius(value);
                }}
                value={realRadius}
                placeholder={"0"}
                negative={false}
                decimal={0}
              >
                <input className="input-number-of-nodes" style={{marginTop: '15px'}}/>
              </NumPad.Number>
              <Button
                style={styles.generateButton}
                variant="secondary"
                onClick={findRadiusDistances}
                disabled={!firstTaskDataIsPrepared}
              >
                Посчитать расстояния
              </Button>
              <Form.Check
                inline
                label="Радиус"
                checked={isRealRadiusExists}
                onChange={() => setIsRealRadiusExists(!isRealRadiusExists)}
              />
            </div>
          </Container>
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          {/* вав */}
          <Button
            style={styles.clearButton}
            variant="danger"
            onClick={clearAll}
          >
            Очистить
          </Button>
        </div>
        <Map
          center={kazanCenterPosition}
          zoom={13}
          className={loading ? "map map-disabled" : "map"}
          id="map"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          />
          {listOfNodes.map((item, key) =>
            mapDisplayFilter.nodes ? (
              <Circle
                center={item}
                radius={10}
                color={key === 0 ? "green" : "red"}
              >
                {key === 0 ? (
                  <></>
                ) : (
                  <Marker icon={HomeIcon} position={item}>
                    <Popup>
                      {item[0]}
                      <br />
                      {item[1]}
                    </Popup>
                  </Marker>
                )}
              </Circle>
            ) : (
              <></>
            )
          )}
          {initialDataIsPrepared && (
            <Circle
              center={listOfNodes[0]}
              radius={10}
              color="green"
              style={{ zIndex: "1000000" }}
            >
              <Marker icon={HospitalIcon} position={listOfNodes[0]}>
                <Popup>
                  {listOfNodes[0][0]}
                  <br />
                  {listOfNodes[0][1]}
                </Popup>
              </Marker>
            </Circle>
          )}
          {shortPathTreeNodes.map((item, key) =>
            mapDisplayFilter.shortPathTree ? (
              <Polyline positions={item} color="red" />
            ) : (
              <></>
            )
          )}
          {listOfTrees.map((item, key) =>
            item.map((item1, key1) =>
              mapDisplayFilter.clusterization && key > 0 ? (
                <Polyline
                  positions={item1}
                  opacity={1}
                  color={key === 0 ? "red" : colorForCluster(key)}
                />
              ) : (
                <></>
              )
            )
          )}
          {clusterNodes.map((item, key) =>
            mapDisplayFilter.clusterization ? (
              <Circle center={item} radius={10} color="black">
                <Marker icon={ClusterIcon} position={item}>
                  <Popup>
                    {item[0]}
                    <br />
                    {item[1]}
                  </Popup>
                </Marker>
              </Circle>
            ) : (
              <></>
            )
          )}
          {homeNodes.map((item, key) =>
            mapDisplayFilter.homesAndHosps ? (
              <Circle center={item} radius={10} color="red">
                <Marker
                  icon={HomeIcon}
                  position={item}
                  onClick={() => handleClick(item)}
                >
                  {/* <Popup>
                    {item[0]}
                    <br />
                    {item[1]}
                  </Popup> */}
                </Marker>
              </Circle>
            ) : (
              <></>
            )
          )}
          {hospNodes.map((item, key) =>
            mapDisplayFilter.homesAndHosps ? (
              <Circle
                center={item}
                radius={10}
                color="red"
                onClick={() => handleClick(item)}
              >
                <Marker
                  icon={HospitalIcon}
                  position={item}
                  onClick={() => handleClick(item)}
                >
                  {/* <Popup>
                    {item[0]}
                    <br />
                    {item[1]}
                  </Popup> */}
                </Marker>
              </Circle>
            ) : (
              <></>
            )
          )}
          {mapDisplayFilter.currentRoute ? (
            <Polyline positions={currentRoute} color="red" />
          ) : (
            <></>
          )}
          {listOfRoutes.map((item, key) =>
            mapDisplayFilter.currentRadiusRoute ? (
              <Polyline positions={item} color="red" />
            ) : (
              <></>
            )
          )}
          {optimalHospitals.map((item, key) =>
            mapDisplayFilter.optimalHospitals ? (
              <Circle center={item} color={retColor(key)} radius={600}>
                <Popup>{retDescription(key)}</Popup>
              </Circle>
            ) : (
              <></>
            )
          )}
          {mapDisplayFilter.minSumHospital && (
            <Circle center={minSumHospital} radius={600} color="red"></Circle>
          )}
          {mapDisplayFilter.shortTreeHospital && (
            <Circle
              center={shortTreeHospital}
              radius={600}
              color="red"
            ></Circle>
          )}
          {isRealRadiusExists && (
            <Circle
              center={selectedHomeCoords}
              radius={realRadius}
              color="green"
            ></Circle>
          )}
          {isRealRadiusExists && (
            <Polyline positions={routesWithinRadius} color="red"/>
          )}
        </Map>
        {loading && (
          <RingLoader
            css={styles.loading}
            size={250}
            color={"#0dcf9b"}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

export default App;
