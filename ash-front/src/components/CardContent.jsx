import React, { useContext, useEffect, useState } from "react";
import { Card, CardBody } from "@nextui-org/react";

export default function CardContent({
  setChangeTopic,
  setTopic,
  topic,
  newData,
  setNewData,
}) {
  const handlechangeTopic = (name, item) => {
    // console.log(newData);
    setChangeTopic(true);
    setTopic([...topic, name]);
    setNewData([]);
    if (item != null) {
      setNewData([...item]);
    }
  };
  return (
    <>
      {newData.length == 1 &&
        newData[0]?.map((d) => {
          return (
            <>
              {d.benchmark_child.map((d) => {
                return (
                  <>
                    <Card
                      isPressable="true"
                      className="w-fit h-1/2 px-8 m-[1rem] bg-gradient-to-tr from-blue-500 to-yellow-500 cursor-pointer"
                      key={d._id}
                      onPress={() => {
                        handlechangeTopic(d.benchmark_name, d.benchmark_child);
                      }}
                    >
                      <CardBody>
                        <p className="text-center text-black/90 text-[1rem] font-bold">
                          {d.benchmark_no}: {d.benchmark_name}
                        </p>
                        <div></div>
                      </CardBody>
                    </Card>
                  </>
                );
              })}
            </>
          );
        })}

      {newData.length > 1 &&
        newData?.map((d) => {
          return (
            <Card
              isPressable="true"
              className="w-fit h-1/2 px-8 m-[1rem] bg-gradient-to-tr from-blue-500 to-yellow-500 cursor-pointer"
              key={d._id}
              onPress={() => {
                handlechangeTopic(d.benchmark_name);
              }}
            >
              <CardBody>
                <p className="text-center text-black/90 text-[1rem] font-bold">
                  {d.benchmark_no}: {d.benchmark_name}
                </p>
                <p
                  className="text-center text-black/90 text-[1rem]"
                  style={{ whiteSpace: "pre-wrap", textAlign: "left" }}
                >
                  {d.benchmark_detail}
                </p>
                <div></div>
              </CardBody>
            </Card>
          );
        })}
      {newData != 1 && newData[0]?.benchmark_detail != null && <p>yes</p>}
    </>
  );
}
