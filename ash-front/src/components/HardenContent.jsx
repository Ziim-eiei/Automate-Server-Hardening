import React, { useState, useEffect } from "react";
import { Card, CardBody, Checkbox, Input } from "@nextui-org/react";
import { Accordion, AccordionItem } from "@nextui-org/react";
import { color } from "framer-motion";
import "../css/Card.css";

function HardenContent({
  setChangeTopic,
  setTopic,
  topic,
  newData,
  checkData,
  setCheckData,
  serverId,
}) {
  const [name, setName] = useState("");
  const [history, setHistory] = useState({});
  useEffect(() => {
    async function getServer() {
      let test_name = "";
      if (serverId) {
        const server = await fetch(
          `http://localhost:8000/api/servers/${serverId}`
        ).then((res) => res.json());
        // console.log(server);
        setName(server["_id"]);
        test_name = server["_id"];
        setHistory(
          JSON.parse(localStorage.getItem(`${test_name}-history`))
            ? JSON.parse(localStorage.getItem(`${test_name}-history`))
            : {}
        );
      }
    }
    getServer();
  }, []);
  // console.log(name);
  // console.log(history);

  const topic_value = ["1.1.2", "1.1.3", "1.1.4", "1.2.1", "1.2.2", "1.2.3"];
  const suggest_value = {
    "1.1.2": 365,
    "1.1.3": 1,
    "1.1.4": 14,
    "1.2.1": 15,
    "1.2.2": 5,
    "1.2.3": 15,
  };
  const info_value = [];
  const handleCheck = (no, value) => {
    const key = `rule_${no.replace(/\./g, "_")}`;
    history[key] = value;
    setHistory({ ...history });
    localStorage.setItem(`${name}-history`, JSON.stringify(history));
    // console.log(history);
    if (!checkData.hasOwnProperty(key)) {
      checkData[key] = true;
      setCheckData(checkData);
      localStorage.setItem(name, JSON.stringify(checkData));
      if (!checkData[`rule_${no.replace(/\./g, "_")}_value`]) {
        checkData[`rule_${no.replace(/\./g, "_")}_value`] = suggest_value[no];
        setCheckData(checkData);
        localStorage.setItem(name, JSON.stringify(checkData));
      }
    } else {
      if (checkData[key + "_value"]) {
        delete history[key + "_value"];
        setHistory({ ...history });
        localStorage.setItem(`${name}-history`, JSON.stringify(history));
        delete checkData[key + "_value"];
      }
      delete checkData[key];
      setCheckData(checkData);
      localStorage.setItem(name, JSON.stringify(checkData));
      const data = JSON.parse(localStorage.getItem(name));
      if (Object.keys(data) == 0) {
        setCheckData({});
        localStorage.removeItem(name);
      }
    }
  };
  const handleValue = (no, value) => {
    // console.log(`${no}: ${value}`);
    value = Math.max(1, Math.min(999, Number(value)));
    const key = `rule_${no.replace(/\./g, "_")}_value`;
    history[key] = value;
    setHistory({ ...history });
    localStorage.setItem(`${name}-history`, JSON.stringify(history));
    // console.log(history);
    checkData[key] = value;
    setCheckData(checkData);
    localStorage.setItem(name, JSON.stringify(checkData));
  };
  const handlechangeTopic = (name, no) => {
    setChangeTopic(true);
    setTopic([...topic, { no: no, name: name }]);
  };
  useEffect(() => {
    setCheckData(
      JSON.parse(localStorage.getItem(name))
        ? JSON.parse(localStorage.getItem(name))
        : {}
    );
    setHistory(history);
  }, [history]);
  // useEffect(() => {

  const render = (d) => {
    return (
      <>
        {d.benchmark_detail ? (
          <Accordion
            variant="splitted"
            style={{ padding: "0px" }}
            classNames={{ title: "py-3" }}
          >
            <AccordionItem
              classNames={{ title: "text-[#E8E8FC] text-[16px] bg-[#2E2E48]" }}
              style={{
                backgroundColor: "#2E2E48",
                marginBottom: "10px",
                padding: "0px 27px",
              }}
              id={d.benchmark_no}
              title={
                d.benchmark_no + " " + d.benchmark_name &&
                topic_value.find((t) => t == d.benchmark_no) &&
                checkData[`rule_${d.benchmark_no.replace(/\./g, "_")}`] ? (
                  <>{d.benchmark_no + " " + d.benchmark_name }  <p style={{color:"aqua", display:"inline"}}>[Editable]</p></>
                ) : (
                  d.benchmark_no + " " + d.benchmark_name
                )
              }
              startContent={
                name != "" && d.benchmark_detail && d.benchmark_no != "2.1" ? (
                  <Checkbox
                    onChange={(e) => {
                      handleCheck(d.benchmark_no, e.target.checked);
                    }}
                    value={history}
                    isSelected={
                      history[`rule_${d.benchmark_no.replace(/\./g, "_")}`]
                    }
                  ></Checkbox>
                ) : null
              }
            >
              {d.benchmark_detail &&
              topic_value.find((t) => t == d.benchmark_no) ? (
                <p className="content-detail">
                  <span className="font-bold">Detail:</span>
                  {d.benchmark_detail}
                  {checkData[`rule_${d.benchmark_no.replace(/\./g, "_")}`] ? (
                    <Input
                      type="number"
                      classNames={{
                        inputWrapper: "h-unit-10 w-[4.5rem]",
                      }}
                      min="1"
                      max="999"
                      value={
                        checkData[
                          `rule_${d.benchmark_no.replace(/\./g, "_")}_value`
                        ]
                      }
                      onChange={(e) => {
                        handleValue(d.benchmark_no, e.target.valueAsNumber);
                      }}
                    />
                  ) : null}
                </p>
              ) : (
                <>
                  <p className="content-detail">
                    <span className="font-bold">Detail:</span> {""}
                    {d.benchmark_detail}
                  </p>
                </>
              )}
            </AccordionItem>
          </Accordion>
        ) : (
          <Card
            isPressable={d.benchmark_detail ? false : true}
            className="content-card-noneCheckBox cursor-pointer"
            key={d._id}
            onPress={() => {
              handlechangeTopic(d.benchmark_name, d.benchmark_no);
            }}
          >
            <CardBody>
              {name != "" && d.benchmark_detail && d.benchmark_no != "2.1" ? (
                <p className="content-card ">
                  {/* <input
                 type="checkbox"
                 onChange={(e) => {
                   handleCheck(d.benchmark_no, e.target.checked);
                 }}
                 value={history}
                 checked={
                   history[`rule_${d.benchmark_no.replace(/\./g, "_")}`]
                 }
               /> */}
                  <Checkbox
                    onChange={(e) => {
                      handleCheck(d.benchmark_no, e.target.checked);
                    }}
                    value={history}
                    isSelected={
                      history[`rule_${d.benchmark_no.replace(/\./g, "_")}`]
                    }
                  ></Checkbox>
                </p>
              ) : null}
              <p className="SubText">
                {d.benchmark_no} {d.benchmark_name}
              </p>
              {d.benchmark_detail ? (
                <p className="text-black/90 text-[1rem]">
                  <span className="font-bold">Detail:</span> {""}
                  {d.benchmark_detail}
                </p>
              ) : null}
              {topic_value.find((t) => t == d.benchmark_no) &&
              checkData[`rule_${d.benchmark_no.replace(/\./g, "_")}`] ? (
                <p className=" text-black/90 text-[1rem]">
                  {/* <input
                 type="number"
                 onChange={(e) => {
                   handleValue(d.benchmark_no, e.target.valueAsNumber);
                 }}
                 value={
                   checkData[
                     `rule_${d.benchmark_no.replace(/\./g, "_")}_value`
                   ]
                 }
                 min="1"
                 max="999"
               /> */}
                  <br />
                  <Input
                    type="number"
                    classNames={{
                      inputWrapper: "h-unit-10 w-[4.5rem]",
                    }}
                    min="1"
                    max="999"
                    value={
                      checkData[
                        `rule_${d.benchmark_no.replace(/\./g, "_")}_value`
                      ]
                    }
                    onChange={(e) => {
                      handleValue(d.benchmark_no, e.target.valueAsNumber);
                    }}
                  />
                </p>
              ) : null}
            </CardBody>
          </Card>
        )}
      </>
    );
  };

  // }, [checkData]);
  return (
    <div
      className="text-white flex flex-col content"
      style={{ whiteSpace: "pre-wrap" }}
    >
      {newData?.map((d) => {
        return <>{render(d)}</>;
      })}
    </div>
  );
}

export default HardenContent;
