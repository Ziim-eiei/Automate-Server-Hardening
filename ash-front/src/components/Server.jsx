import React from "react";
import { MyInput } from "./Input";

export default function Server({ server, setServer }) {
  const handleIpChange = (e) => {
    setServer({ ...server, ip: e.target.value });
  };
  const handleUsernameChange = (e) => {
    setServer({ ...server, username: e.target.value });
  };
  const handlePasswordChange = (e) => {
    setServer({ ...server, password: e.target.value });
  };
  return (
    <div>
      <MyInput
        radius="full"
        className="w-[20rem] p-2"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Server IP :"
        labelPlacement="outside"
        placeholder="Example: 192.168.x.x"
        value={server.ip}
        onChange={handleIpChange}
      />
      <MyInput
        radius="full"
        className="w-[20rem] p-2"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Username :"
        placeholder="username"
        labelPlacement="outside"
        value={server.username}
        onChange={handleUsernameChange}
      />
      <MyInput
        radius="full"
        className="w-[20rem] p-2"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Password :"
        placeholder="passsword"
        labelPlacement="outside"
        value={server.password}
        onChange={handlePasswordChange}
        type="password"
      />
    </div>
  );
}
