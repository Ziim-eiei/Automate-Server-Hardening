import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Divider,
  Link,
  Image,
} from "@nextui-org/react";

// import "../css/index.css";
import "../css/Card.css";
import SideBar from "./SideBar";
import HardenTopper from "./HardenTopper";
import HardenContent from "./HardenContent";
function AuditCard() {
  const [changeTopic, setChangeTopic] = useState(false);
  const [topic, setTopic] = useState([{ no: 0, name: "Topics" }]);
  const [newData, setNewData] = useState([]);
  const [checkData, setCheckData] = useState({});
  const [isPressHarden, setIsPressHarden] = useState(false);
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
    }
  }, [isPressHarden]);
  const { serverId } = useParams();
  // console.log(serverId);
  return (
    <Card className="CardAudit">
      <CardBody className="CardBody">
        <div className="Container">
          <div className="SideBar-Container">
            <SideBar />
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
            />
          </div>
          <div className="Content-Container">
            <HardenContent
              setChangeTopic={setChangeTopic}
              topic={topic}
              setTopic={setTopic}
              newData={newData}
              checkData={checkData}
              setCheckData={setCheckData}
              serverId={serverId}
            />

          </div>
        </div>
      </CardBody>
    </Card>
  );
}

export default AuditCard;
