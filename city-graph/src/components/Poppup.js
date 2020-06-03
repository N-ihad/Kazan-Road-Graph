import React, { useState } from "react";
// import Popup from "reactjs-popup";
import { Button, Modal } from "react-bootstrap";

const Poppup = ({ infoToShow, clusterInfo }) => {
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <Button
        variant="primary"
        onClick={handleShow}
        style={{ marginTop: "15px" }}
      >
        Подробности
      </Button>

      <Modal show={show} onHide={handleClose} style={{ marginTop: "50px" }}>
        <Modal.Header closeButton>
          <Modal.Title>Дополнительная информация</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h4>Дерево кратчайших путей</h4>
          <span> {"Вес дерева: " + infoToShow.treeWeight} </span>
          <br />
          <span> {"Длина путей: " + infoToShow.pathLength} </span>
        </Modal.Body>
        <hr style={{ border: "1px solid grey", width: "100%", padding: '0px', margin: '0px' }} />
        <Modal.Body>
          <h4>Кластеризация</h4>
          <hr />
          <h5 style={{marginBottom: '8px'}}>2 Кластера</h5>
          <span> {"Вес дерева: " + clusterInfo.cluster2.treeWeight} </span>
          <br />
          <span> {"Длина путей: " + clusterInfo.cluster2.pathLength} </span>
          <hr />
          <h5 style={{marginBottom: '8px'}}>3 Кластера</h5>
          <span> {"Вес дерева: " + clusterInfo.cluster3.treeWeight} </span>
          <br />
          <span> {"Длина путей: " + clusterInfo.cluster3.pathLength} </span>
          <hr />
          <h5 style={{marginBottom: '8px'}}>5 Кластера</h5>
          <span> {"Вес дерева: " + clusterInfo.cluster5.treeWeight} </span>
          <br />
          <span> {"Длина путей: " + clusterInfo.cluster5.pathLength} </span>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Закрыть
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default Poppup;
