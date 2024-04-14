import React, { useState, useRef, useEffect } from "react";
import { Card, CardBody } from "@nextui-org/react";
import { MyButton } from "../components/Button";
import Project from "../components/Project";
import Server from "../components/Server";
import { useNavigate, useParams } from "react-router-dom";
import "../css/Edit.css";

export default function EditPage() {
  let { state, id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState({ name: "", description: "" });
  const [server, setServer] = useState({ ip: "", username: "", password: "" });
  const his_project = useRef({ name: "", description: "" });
  const his_server = useRef({ ip: "", username: "", password: "" });
  const invalidIP = useRef(false);
  async function fetchData() {
    if (state === "project") {
      const data = await fetch(`http://localhost:8000/api/projects/${id}`).then(
        (res) => res.json()
      );
      setProject({
        name: data.project_name,
        description: data.project_description,
      });
      his_project.current = {
        name: data.project_name,
        description: data.project_description,
      };
    } else if (state === "server") {
      const data = await fetch(`http://localhost:8000/api/servers/${id}`).then(
        (res) => res.json()
      );
      // console.log(data);
      setServer({
        ip: data.server_ip,
        username: data.server_username,
        password: data.server_password,
      });
      his_server.current = {
        ip: data.server_ip,
        username: data.server_username,
        password: data.server_password,
      };
    }
  }
  useEffect(() => {
    fetchData();
  }, []);
  function updateProject() {
    fetch(`http://localhost:8000/api/projects/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_name: project.name,
        project_description: project.description,
      }),
    }).then((res) => {
      if (res.status === 200) {
        navigate("/project");
      }
    });
  }
  function updateServer() {
    fetch(`http://localhost:8000/api/servers/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        server_ip: server.ip,
        server_username: server.username,
        server_password: server.password,
      }),
    }).then((res) => {
      if (res.status === 200) {
        history.go(-1);
      }
    });
  }
  function render() {
    switch (state) {
      case "project":
        return (
          <Project project={project} setProject={setProject} edit={true} />
        );
      case "server":
        return (
          <Server
            server={server}
            setServer={setServer}
            invalidIP={invalidIP}
            edit={true}
          />
        );
      default:
        window.location.href = "/error";
    }
  }
  function checkProject() {
    if (
      project.name != his_project.current.name ||
      project.description != his_project.current.description
    ) {
      if (project.name && project.description) return false;
      else return true;
    } else {
      return true;
    }
  }
  function checkServer() {
    if (
      server.ip != his_server.current.ip ||
      server.username != his_server.current.username ||
      server.password != his_server.current.password
    ) {
      if (server.ip && !invalidIP.current && server.password && server.username)
        return false;
      else return true;
    } else {
      return true;
    }
  }
  return (
    <>
      <div className="container flex justify-center items-center editBg ">
        <Card className="vertical-center rounded-3xl">
          <CardBody>
            <div>{render()}</div>
            <div className="text-right">
              <MyButton
                className=" bg-[#4A3AFF] text-[#FFFFFF] shadow-xl py-4 px-8 rounded-xl "
                onClick={() => {
                  switch (state) {
                    case "project":
                      updateProject();
                      break;
                    case "server":
                      updateServer();
                      break;
                    default:
                      break;
                  }
                }}
                isDisabled={checkProject() && checkServer()}
              >
                Update
              </MyButton>
            </div>
          </CardBody>
        </Card>
        <div class="dotEdit"></div>
      </div>
    </>
  );
}
