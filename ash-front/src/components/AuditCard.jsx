import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { Card, CardBody } from "@nextui-org/react";

// import "../css/index.css";
import "../css/Card.css";
import SideBar from "./SideBar";
import HardenTopper from "./HardenTopper";
import HardenContent from "./HardenContent";
import { Spinner } from "@nextui-org/react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
} from "@nextui-org/react";

function AuditCard() {
  const { isOpen, onOpenChange, onOpen } = useDisclosure();
  const [changeTopic, setChangeTopic] = useState(false);
  const [topic, setTopic] = useState([{ no: 0, name: "Topics" }]);
  const [newData, setNewData] = useState([]);
  const [checkData, setCheckData] = useState({});
  const [isPressHarden, setIsPressHarden] = useState(false);
  const [run, setRun] = useState(false);
  // const [serverId, setServerId] = useState("");

  // console.log(serverId);
  const newFecth = async () => {
    let no = "";
    if (topic.length > 1) {
      no = topic[topic.length - 1]["no"];
    } else {
      no = "";
    }
    const nd = await fetch(`http://localhost:8000/api/documents/${no}`).then(
      (res) => res.json()
    );
    if (nd?.length) {
      setNewData([...nd]);
    }
  };
  useEffect(() => {
    newFecth();
  }, [topic]);
  useEffect(() => {
    async function runHarden() {
      setRun(true);
      const job = await fetch("http://localhost:8000/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          server_id: serverId,
          type: "hardening",
        }),
      }).then((res) => res.json());
      // console.log(job);
      const run = await fetch("http://localhost:8000/api/hardening", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          server_id: serverId,
          topic_select: checkData,
        }),
      }).then((res) => res.json());
      // console.log(run);
    }
    if (isPressHarden) {
      // console.log(checkData);
      if (Object.keys(checkData).length != 0) {
        runHarden();
      }
      setIsPressHarden(false);
      setMessage([]);
    }
  }, [isPressHarden]);
  const { serverId } = useParams();
  const ws = useRef(null);
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/api/ws");
    ws.current = socket;
    ws.current.onmessage = (e) => {
      // setMessage(...message, e.data);
      setMessage((prev) => [...prev, e.data]);
    };
  }, []);
  const [message, setMessage] = useState([]);
  const endOfMessageRef = useRef(null);
  useEffect(() => {
    endOfMessageRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [message?.length]);
  return (
    <Card className="CardAudit">
      <CardBody className="CardBody">
        <div className="Container">
          <div className="SideBar-Container">
            <SideBar serverId={serverId} />
          </div>
          <div className="Heading-Container">
            <HardenTopper
              changeTopic={changeTopic}
              topic={topic}
              setTopic={setTopic}
              setIsPressHarden={setIsPressHarden}
              serverId={serverId}
              isPressHarden={isPressHarden}
              checkData={checkData}
              onOpen={onOpen}
            />
          </div>
          <div className="Content-Container example">
            <HardenContent
              setChangeTopic={setChangeTopic}
              topic={topic}
              setTopic={setTopic}
              newData={newData}
              checkData={checkData}
              setCheckData={setCheckData}
              serverId={serverId}
              onOpen={onOpen}
              run={run}
              setRun={setRun}
            />
          </div>
          <Modal
            isOpen={isOpen}
            onOpenChange={onOpenChange}
            isDismissable={false}
            scrollBehavior="inside"
            size="5xl"
          >
            <ModalContent>
              {(onClose) => (
                <>
                  <ModalHeader className="flex flex-col gap-3">
                    Result of Hardening
                  </ModalHeader>
                  <ModalBody className="px-[8rem] bg-[#27273D]">
                    {message != "" ? "" : <Spinner color="white" />}
                    <p className="whitespace-pre-wrap text-left text-white">
                      {message}
                      <div ref={endOfMessageRef} />
                    </p>
                  </ModalBody>
                  <ModalFooter>
                    <Button
                      color="danger"
                      onPress={() => {
                        onClose();
                        history.go(0);
                      }}
                    >
                      Close
                    </Button>
                  </ModalFooter>
                </>
              )}
            </ModalContent>
          </Modal>
        </div>
      </CardBody>
    </Card>
  );
}

export default AuditCard;
