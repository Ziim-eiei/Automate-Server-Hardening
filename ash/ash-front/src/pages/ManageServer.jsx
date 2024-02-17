import React from "react";
import SideBar from "../components/SideBar";
import { Card, CardBody } from "@nextui-org/react";
import ServerContent from "../components/ServerContent";
import ServerTopper from "../components/ServerTopper";

export default function ManageServer() {
  return (
    <Card className="CardAudit">
      <CardBody className="CardBody">
        <div className="Container">
          <div className="SideBar-Container">
            <SideBar />
          </div>
          <div className="Heading-Container">
            <ServerTopper />
          </div>
          <div className="Content-Container">
            <ServerContent />
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
