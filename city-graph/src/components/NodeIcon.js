import { Icon } from "leaflet";

const HospitalIcon = new Icon({
  iconUrl: require("./hospital.svg"),
  iconRetinaUrl: require("./hospital.svg"),
  iconSize: [40, 40], // size of the icon
  shadowSize: [50, 64], // size of the shadow
});

const HomeIcon = new Icon({
  iconUrl: require("./home.svg"),
  iconRetinaUrl: require("./home.svg"),
  iconSize: [30, 30], // size of the icon
  shadowSize: [50, 64], // size of the shadow
});

const ClusterIcon = new Icon({
  iconUrl: require("./cluster.svg"),
  iconRetinaUrl: require("./cluster.svg"),
  iconSize: [40, 40], // size of the icon
  shadowSize: [50, 64], // size of the shadow
});

export { HospitalIcon, HomeIcon, ClusterIcon };
