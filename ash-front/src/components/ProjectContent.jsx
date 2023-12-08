import React from "react";
import { Card, CardBody } from "@nextui-org/react";
import useSWR from "swr";
import { useNavigate } from "react-router-dom";
import { MyButton } from "../components/Button";

export default function ProjectContent() {
  const navigate = useNavigate();
  const fetcher = (...args) => fetch(...args).then((res) => res.json());
  const { data } = useSWR("http://localhost:8000/api/projects", fetcher);
  const deleteProject = async (id) => {
    const data = await fetch(`http://localhost:8000/api/projects/${id}`, {
      method: "DELETE",
    }).then((res) => res.json());
  };
  return (
    <div className="text-white flex flex-col justify-center items-center p-10">
      {data?.map((d) => {
        return (
          <Card
            className="w-fit h-1/2 px-8 m-[1rem] bg-gradient-to-tr from-blue-500 to-yellow-500 cursor-pointer"
            key={d._id}
            isPressable="true"
            onPress={() => {
              navigate(`/server/${d._id}`);
            }}
          >
            <CardBody>
              <p className="text-center text-black/90 text-[1rem] font-bold">
                Project name: {d.project_name}
              </p>
              <p className="text-center text-black/90 text-[1rem]">
                Project description: {d.project_description}
              </p>
              <p className="text-center text-black/90 text-[1rem]">
                Server amount: {d.server.length}
              </p>
              <div>
                <MyButton
                  onClick={() => {
                    deleteProject(d._id);
                    window.location.reload();
                  }}
                >
                  Delete
                </MyButton>
              </div>
            </CardBody>
          </Card>
        );
      })}
      {data?.length == 0 && (
        <div>
          <p>Don't have server</p>
          <MyButton
            onClick={() => {
              navigate("..");
            }}
          >
            Create project
          </MyButton>
        </div>
      )}
    </div>
  );
}
