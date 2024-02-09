import React from "react";
import SideBar from "../components/SideBar";
import { Card, CardBody } from "@nextui-org/react";
import HistoryTopper from "../components/HistoryTopper";
import HistoryContent from "../components/HistoryContent";

export default function HistoryPage() {
  return (
    <Card className="CardAudit">
      <CardBody className="CardBody">
        <div className="Container">
          <div className="SideBar-Container">
            <SideBar />
          </div>
          <div className="Heading-Container">
            <HistoryTopper />
          </div>
          <div className="Content-Container">
            <HistoryContent />
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
