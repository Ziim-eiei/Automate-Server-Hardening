import React, { useRef, useState } from "react";
import { Card, CardBody } from "@nextui-org/react";
import { MyButton } from "../components/Button";
import Project from "../components/Project";
import Server from "../components/Server";
import { useNavigate, useParams } from "react-router-dom";

export default function CreateProject() {
  let { state, project_id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState({ name: "", description: "" });
  const [server, setServer] = useState({ ip: "", username: "", password: "" });
  const invalidIP = useRef(false);
  const createProjectId = useRef(null);
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
    createProjectId.current = dataProject._id;
    // console.log(dataProject);
  };
  const createServer = async () => {
    if (project_id || createProjectId.current) {
      const dataServer = await fetch("http://localhost:8000/api/servers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_id: project_id || createProjectId.current,
          server_ip: server.ip,
          server_username: server.username,
          server_password: server.password,
        }),
      }).then((res) => res.json());
      // console.log(dataServer);
    }
  };
  //post project
  //post server
  function render() {
    switch (state) {
      case "project":
        return <Project project={project} setProject={setProject} />;
      case "server":
        return (
          <Server server={server} setServer={setServer} invalidIP={invalidIP} />
        );
      default:
        window.location.href = "/error";
    }
  }
  function checkProject() {
    if (project.name && project.description) {
      return false;
    } else {
      return true;
    }
  }
  function checkServer() {
    if (server.ip && server.username && server.password) {
      return false;
    } else {
      return true;
    }
  }
  return (
    <>
      <div className="text-white flex justify-center items-center p-10">
        <Card className="w-fit h-1/2 px-8 bg-gradient-to-tr from-blue-500 to-yellow-500">
          <CardBody>
            <p className="text-center text-black/90 text-xl font-bold">
              Automate Server Hardening
            </p>
            <div>{render()}</div>
            <div className="text-right">
              <MyButton
                onClick={() => {
                  switch (state) {
                    case "project":
                      createProject();
                      history.go(-1);
                      break;
                    case "server":
                      createServer();
                      history.go(-1);
                      break;
                    default:
                      break;
                  }
                }}
                isDisabled={
                  (checkProject() && checkServer()) || invalidIP.current
                }
              >
                Create
              </MyButton>
            </div>
          </CardBody>
        </Card>
      </div>
    </>
  );
}
