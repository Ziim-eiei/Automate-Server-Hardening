import React from "react";
import { Card, CardHeader, CardBody, CardFooter, Divider, Link, Image } from "@nextui-org/react";
import SideBar from "./SideBar";
import HardenTopper from "./HardenTopper";
import '../css/cards.css'
import useSWR from 'swr'

function CardAudit() {
    const fetcher = (...args) => fetch(...args).then(res => res.json())
    const { data, error, isLoading } = useSWR('http://localhost:8000/api/documents', fetcher)
    return (
        <Card className="max-w-[400px] cardAudit" >
            {/* <CardHeader className="flex gap-3" ></CardHeader> */}
            {/* <Divider /> */}

            <CardBody className="CardBody">
                <SideBar />
                <HardenTopper />
                <div className="text-white" style={{whiteSpace:"pre-wrap",textAlign:"left"}}>
                {data?.map((item)=>{
                    return (
                    <li key={item._id}>
                        no: {item.benchmark_no} <br />
                        topic: {item.benchmark_name} <br />
                        {/* child: {item.benchmark_child?.map((item2)=>{
                        return item2.benchmark_child?.map(item3=>{
                            return <li key={item3.benchmark_no}>{item3.benchmark_no}</li>
                        })
                        })} */}
                    </li>
                    )
                })}
             </div>
            </CardBody>

            {/* <Divider /> */}
            {/* <CardFooter/> */}
        </Card>

    );
}

export default CardAudit