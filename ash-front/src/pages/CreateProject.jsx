import React, { useState } from "react";
import { Card, CardBody } from "@nextui-org/react";
import { MyButton } from "../components/Button";
import Project from "../components/Project";
import Server from "../components/Server";
import { useNavigate } from "react-router-dom";

export default function CreateProject() {
  const navigate = useNavigate();
  const [project, setProject] = useState({ name: "", description: "" });
  const [server, setServer] = useState({ ip: "", username: "", password: "" });
  const [isNext, setIsNext] = useState(false);
  const createProject = async () => {
    const dataProject = await fetch("http://localhost:8000/api/projects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_name: project.name,
        project_description: project.description,
      }),
    }).then((res) => res.json());
    console.log(dataProject);
    const dataServer = await fetch("http://localhost:8000/api/servers", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_id: dataProject._id,
        server_ip: server.ip,
        server_username: server.username,
        server_password: server.password,
      }),
    }).then((res) => res.json());
    // console.log(dataServer);
    navigate("/project");
  };
  //post project
  //post server
  return (
    <>
      <div className="text-white flex justify-center items-center p-10">
        <Card className="w-fit h-1/2 px-8 bg-gradient-to-tr from-blue-500 to-yellow-500">
          <CardBody>
            <p className="text-center text-black/90 text-xl font-bold">
              Automate Server Hardening
            </p>
            <div>
              {isNext ? (
                <Server server={server} SetServer={setServer} />
              ) : (
                <Project setProject={setProject} project={project} />
              )}
            </div>
            <div className="text-right">
              {isNext ? (
                <MyButton onClick={() => createProject()}>Create</MyButton>
              ) : (
                <MyButton onClick={() => setIsNext(true)}>Next</MyButton>
              )}
            </div>
          </CardBody>
        </Card>
      </div>
      {/* <div className="text-white">
        <p>project name: {project.name}</p>
        <p>project desc: {project.description}</p>
        <p>server ip: {server.ip}</p>
        <p>server user: {server.username}</p>
        <p>server pass: {server.password}</p>
      </div> */}
    </>
  );
}
