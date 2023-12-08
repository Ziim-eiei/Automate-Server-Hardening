import React from "react";
import { MyInput } from "./Input";

export default function CreateProject({ setProject, project }) {
  const handleNameChange = (e) => {
    setProject({ ...project, name: e.target.value });
  };
  const handleDescChange = (e) => {
    setProject({ ...project, description: e.target.value });
  };
  return (
    <div>
      <MyInput
        radius="full"
        className="w-[20rem] p-2"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Project Name :"
        labelPlacement="outside"
        placeholder="Name"
        value={project.name}
        onChange={handleNameChange}
      />
      <MyInput
        radius="full"
        className="w-[20rem] p-2"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Project Description :"
        placeholder="Description"
        labelPlacement="outside"
        value={project.description}
        onChange={handleDescChange}
      />
    </div>
  );
}
