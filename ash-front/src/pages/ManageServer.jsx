import React from "react";
import SideBar from "../components/SideBar";
import ProjectTopper from "../components/ProjectTopper";
import { Card, CardBody } from "@nextui-org/react";
import ServerContent from "../components/ServerContent";

export default function ManageServer() {
  return (
    <Card className="CardAudit">
      <CardBody className="CardBody">
        <div className="Container">
          <div className="SideBar-Container">
            <SideBar />
          </div>
          <div className="Heading-Container">
            <ProjectTopper />
          </div>
          <div className="Content-Container">
            <ServerContent />
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
