import React, { useEffect, useState } from "react";
import { Breadcrumbs, BreadcrumbItem } from "@nextui-org/react";
import { MyButton } from "../components/Button";

function HardenTopper({
  changeTopic,
  topic,
  setTopic,
  setIsPressHarden,
  serverId,
  checkData,
}) {
  // let { serverId } = useParams();
  const [data, setData] = useState("");

  useEffect(() => {
    async function getInfo() {
      if (serverId != null) {
        // console.log("yes");
        // setServerId(serverId);
        const server = await fetch(
          `http://localhost:8000/api/servers/${serverId}`
        ).then((res) => res.json());
        const project = await fetch(
          `http://localhost:8000/api/projects/${server["project_id"]}`
        ).then((res) => res.json());
        setData(project);
      } else {
        // serverId("");
        // console.log("no");
      }
    }
    getInfo();
  }, []);
  const handleClick = (name) => {
    // console.log(name);
    if (topic.length != 0) {
      const index = topic.findIndex((t) => t.name == name);
      // console.log(index);
      topic = topic.slice(0, index + 1);
      // console.log(topic);
      setTopic([...topic]);
    } else {
      // console.log();
    }
  };
  // console.log(serverId);
  return (
    <span className="topper">
      {changeTopic && topic?.length > 1 ? (
        <Breadcrumbs
          className="heading"
          itemClasses={{
            item: "text-white/60 data-[current=true]:text-white text-[1.1rem]",
            separator: "text-white/40",
          }}
        >
          {topic?.map((t) => {
            return (
              <BreadcrumbItem
                key={t.no}
                onPress={() => {
                  handleClick(t.name);
                }}
              >
                {t.name}
              </BreadcrumbItem>
            );
          })}
        </Breadcrumbs>
      ) : (
        <h1 className="heading">Select topic to Hardening & Audit</h1>
      )}
      {serverId ? (
        <>
          <p className="projName">Project name: {data?.project_name}</p>
          <div className="projName p-10">
            <MyButton
              onClick={() => {
                setIsPressHarden(true);
                // setServerId(serverId);
              }}
              isDisabled={Object.keys(checkData).length != 0 ? false : true}
            >
              Hardening
            </MyButton>
          </div>
        </>
      ) : (
        <>
          <p className="projName text-danger">Please choose server</p>
        </>
      )}

      <div className="row">
        <p className="col topper-name">Name</p>
        <input className="topper-search" placeholder="Type to search..." />
      </div>
    </span>
  );
}

export default HardenTopper;
