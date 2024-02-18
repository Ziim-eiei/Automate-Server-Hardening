import React from "react";
import { MyInput } from "./Input";
import { Textarea } from "@nextui-org/react";

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
      <Textarea
        className="max-w-xl"
        placeholder="Your Description....."
        labelPlacement="outside"
        label="Project Description :"
        onChange={(e) => {
          handleDescChange(e);
        }}
        value={project.description}
      />
      <br />
    </div>
  );
}
