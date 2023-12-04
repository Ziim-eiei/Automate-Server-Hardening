import React from "react";
import { Card, CardHeader, CardBody, CardFooter, Divider, Link, Image } from "@nextui-org/react";

import '../css/index.css'
import '../css/Card.css'
import SideBar from "./SideBar";
import HardenTopper from "./HardenTopper";
import HardenContent from "./HardenContent";


function AuditCard() {
    return (
        <Card className="CardAudit" >
            <CardBody className="CardBody">
                <div className="Container">
                    <div className="SideBar-Container">
                        <SideBar />
                    </div>
                    <div className="Heading-Container">
                        <HardenTopper />
                    </div>
                    <div className="Content-Container">
                        <HardenContent/>
                    </div>
                </div>
            </CardBody>
        </Card>

    )
}

export default AuditCard