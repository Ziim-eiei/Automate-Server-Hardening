import React, { useRef } from "react";
import { MyInput } from "./Input";

export default function Server({ server, setServer, invalidIP }) {
  function checkIPFormat(ip) {
    const pattern = new RegExp(
      /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    );
    return !pattern.test(ip);
  }
  const message = useRef("");
  const handleIpChange = (e) => {
    if (checkIPFormat(e.target.value) && e.target.value !== "") {
      message.current = "Invalid IP address";
      invalidIP.current = true;
    } else {
      invalidIP.current = false;
      message.current = "";
    }
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
        errorMessage={message.current}
        isInvalid={message.current !== ""}
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
