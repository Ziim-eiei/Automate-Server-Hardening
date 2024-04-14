import React, { useRef } from "react";
import { MyInput } from "./Input";
import "../css/Create.css";

export default function Server({ server, setServer, invalidIP, edit }) {
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
      {edit ? (
        <p className="font-bold text-center text-xl">Edit server</p>
      ) : (
        <p className="font-bold text-center text-xl">Create server</p>
      )}
      <p className="lineBar"></p>
      <MyInput
        className="createServer drop-shadow-sm rounded-2xl"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        radius="md"
        label="Server IP :"
        labelPlacement="outside"
        placeholder="Example: 192.168.x.x"
        variant="bordered"
        value={server.ip}
        onChange={handleIpChange}
        errorMessage={message.current}
        isInvalid={message.current !== ""}
      />
      <MyInput
        className="createServer drop-shadow-sm rounded-2xl"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Username :"
        radius="md"
        placeholder="username"
        labelPlacement="outside"
        variant="bordered"
        value={server.username}
        onChange={handleUsernameChange}
      />
      <MyInput
        className="createServer drop-shadow-sm rounded-2xl"
        classNames={{
          inputWrapper: "h-unit-10",
        }}
        label="Password :"
        radius="md"
        placeholder="passsword"
        labelPlacement="outside"
        variant="bordered"
        value={server.password}
        onChange={handlePasswordChange}
        type="password"
      />
      
    </div>
  );
}
