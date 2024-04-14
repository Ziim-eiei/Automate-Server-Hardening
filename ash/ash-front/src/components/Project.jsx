import React from "react";
import { MyInput } from "./Input";
import { Textarea } from "@nextui-org/react";
import "../css/Create.css";

export default function CreateProject({ setProject, project, edit }) {
  const handleNameChange = (e) => {
    setProject({ ...project, name: e.target.value });
  };
  const handleDescChange = (e) => {
    setProject({ ...project, description: e.target.value });
  };
  // console.log(project);
  return (
    <div className="text-black">
      {edit ? (
        <p className="font-bold text-center text-xl">Edit project</p>
      ) : (
        <p className="font-bold text-center text-xl">Create project</p>
      )}
      <p className="lineBar"></p>
      <MyInput
        className="createName drop-shadow-sm rounded-2xl"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        radius="md"
        label="Project Name :"
        labelPlacement="outside"
        placeholder="Name"
        variant="bordered"
        value={project.name}
        onChange={handleNameChange}
      />
      <Textarea
        className="createDesc drop-shadow-md rounded-2xl"
        placeholder="Your Description"
        labelPlacement="outside"
        label="Project Description :"
        variant="bordered"
        onChange={(e) => {
          handleDescChange(e);
        }}
        value={project.description}
      />
      <br />
    </div>
  );
}
