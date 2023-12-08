import React from "react";
import { Card, CardBody } from "@nextui-org/react";
import useSWR from "swr";
import { useNavigate, useParams } from "react-router-dom";

export default function ServerContent() {
  let { projectId } = useParams();
  const navigate = useNavigate();
  const fetcher = (...args) => fetch(...args).then((res) => res.json());
  const { data } = useSWR(
    `http://localhost:8000/api/projects/${projectId}`,
    fetcher
  );
  return (
    <div className="text-white flex flex-col justify-center items-center p-10">
      {data?.server?.map((d) => {
        return (
          <Card
            className="w-fit h-1/2 px-8 m-[1rem] bg-gradient-to-tr from-blue-500 to-yellow-500 cursor-pointer"
            key={d._id}
            isPressable="true"
            onPress={() => {
              navigate(`/hardening/${d._id}`);
            }}
          >
            <CardBody>
              <p className="text-center text-black/90 text-[1rem] font-bold">
                Sever IP: {d.server_ip}
              </p>
              <p className="text-center text-black/90 text-[1rem]">
                Username: {d.server_username}
              </p>
              <p className="text-center text-black/90 text-[1rem]">
                Password: {d.server_password}
              </p>
              <div></div>
            </CardBody>
          </Card>
        );
      })}
    </div>
  );
}
