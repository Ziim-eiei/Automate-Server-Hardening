import React, { useEffect, useState } from "react";
import { Breadcrumbs, BreadcrumbItem } from "@nextui-org/react";
import { MyButton } from "../components/Button";
// import { SearchIcon } from "./icons/SearchIcon";

function HardenTopper({
  changeTopic,
  topic,
  setTopic,
  setIsPressHarden,
  serverId,
  checkData,
  onOpen,
}) {
  // let { serverId } = useParams();
  const [data, setData] = useState("");

  useEffect(() => {
    async function getInfo() {
      if (serverId != null) {
        // console.log("yes");
        // setServerId(serverId);
        let server_ip = "";
        const server = await fetch(
          `http://localhost:8000/api/servers/${serverId}`
        ).then(async (res) => {
          const data = await res.json();
          server_ip = data.server_ip;
          return data;
        });
        const project = await fetch(
          `http://localhost:8000/api/projects/${server["project_id"]}`
        ).then((res) => res.json());
        console.log(project);
        setData(`${project.project_name} - ${server_ip}`);
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
    <div className="topper">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {changeTopic && topic?.length > 1 ? (
          <Breadcrumbs
            className="heading"
            itemClasses={{
              item: "text-white/60 data-[current=true]:text-white text-[1.375rem]",
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
          <h1 className="heading HeadText">
            Select topic to Hardening & Audit
          </h1>
        )}
        {serverId ? (
          <>
            <p className="projName SubText">Project name: {data}</p>
          </>
        ) : (
          <>
            <p className="projName text-danger">Please choose server</p>
          </>
        )}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <p className="topper-name SubText">Name</p>
        <div>
          {/* <input className="topper-search" placeholder="Type to search..." /> */}

          <MyButton
            className="topper-btn"
            onClick={() => {
              setIsPressHarden(true);
              onOpen();
              // console.log("Hardening");
            }}
            isDisabled={Object.keys(checkData).length != 0 ? false : true}
          >
            Hardening
          </MyButton>
        </div>
      </div>
    </div>
  );
}

export default HardenTopper;
