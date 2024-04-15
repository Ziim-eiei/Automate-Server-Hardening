import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { Card, CardBody } from "@nextui-org/react";
import DeleteIcon from "@mui/icons-material/Delete";
import { Accordion, AccordionItem } from "@nextui-org/react";
import "../css/Card.css";
import SideBar from "./SideBar";
import HardenTopper from "./HardenTopper";
import HardenContent from "./HardenContent";
import { Spinner } from "@nextui-org/react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
} from "@nextui-org/react";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";

function AuditCard() {
  const { isOpen, onOpenChange, onOpen } = useDisclosure();
  const [changeTopic, setChangeTopic] = useState(false);
  const [topic, setTopic] = useState([{ no: 0, name: "Topics" }]);
  const [newData, setNewData] = useState([]);
  const [checkData, setCheckData] = useState({});
  const [isPressHarden, setIsPressHarden] = useState(false);
  const [run, setRun] = useState(false);
  const [isPressSuggestion, setIsPressSuggestion] = useState(false);
  const [modalOneVisible, setModalOneVisible] = useState(false);
  const [modalTwoVisible, setModalTwoVisible] = useState(false);
  const [history, setHistory] = useState({});
  const result_hardening = useRef(null);
  const result_hardening_history = useRef([]);
  const result_hardening_history_failed = useRef([]);
  const run_hardening_success = useRef(false);
  const [message, setMessage] = useState([]);
  const endOfMessageRef = useRef(null);
  const newFecth = async () => {
    let no = "";
    if (topic.length > 1) {
      no = topic[topic.length - 1]["no"];
    } else {
      no = "";
    }
    const nd = await fetch(`http://localhost:8000/api/documents/${no}`).then(
      (res) => res.json()
    );
    if (nd?.length) {
      setNewData([...nd]);
    }
  };
  useEffect(() => {
    newFecth();
  }, [topic]);
  useEffect(() => {
    let jobID = "";
    async function runHarden() {
      setRun(true);
      const job = await fetch("http://localhost:8000/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          server_id: serverId,
          type: "hardening",
        }),
      }).then(async (res) => {
        const data = await res.json();
        jobID = data["job_id"];
      });
      // console.log(jobID);
      if (ws.current.readyState === 1) {
        const run = await fetch("http://localhost:8000/api/hardening", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            job_id: jobID,
            topic_select: checkData,
          }),
        }).then((res) => res.json());
      }
      // console.log(run);
    }
    if (isPressHarden) {
      run_hardening_success.current = false;
      result_hardening.current = "";
      result_hardening_history.current = [];
      result_hardening_history_failed.current = [];
      // console.log(checkData);
      if (Object.keys(checkData).length != 0) {
        runHarden();
        setModalOneVisible(true);
      }
      setIsPressHarden(false);
      setMessage([]);
    }
  }, [isPressHarden]);
  const { serverId } = useParams();
  const ws = useRef(null);
  useEffect(() => {
    // const audit_pattern = /PLAY \[Fetch file from server\] \*+/;
    const socket = new WebSocket("ws://localhost:8000/api/ws");
    ws.current = socket;
    ws.current.onmessage = (e) => {
      setMessage((prev) => [...prev, e.data]);
      result_hardening.current += e.data;
      if (result_hardening.current.includes("PLAY RECAP")) {
        renderHardening();
        run_hardening_success.current = true;
      }
    };
    return () => {
      ws.current.close();
    };
  }, []);
  useEffect(() => {
    endOfMessageRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [message?.length]);
  useEffect(() => {
    if (isPressSuggestion) {
      autoSuggestion();
      setModalTwoVisible(true);
    }
  }, [isPressSuggestion]);
  const autoSuggestionData = useRef("");
  async function autoSuggestion() {
    const data = await fetch("http://localhost:8000/api/audit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        server_id: serverId,
      }),
    }).then(async (res) => {
      if (res.status === 200) {
        const auditData = await fetch(
          "http://localhost:8000/api/audit/" + serverId
        ).then((res) => {
          return res.json();
        });
        autoSuggestionData.current = auditData;
        renderAutoSuggestion(auditData);
      }
    });
    // const auditData = await fetch(
    //   "http://localhost:8000/api/audit/" + serverId
    // ).then((res) => {
    //   return res.json();
    // });
    // renderAutoSuggestion(auditData);
    setIsPressSuggestion(false);
    for (const d in autoSuggestionData.current) {
      if (autoSuggestionData.current[d]["status"] === true) {
        delete autoSuggestionData.current[d];
      }
    }
  }
  const handleSuggestion = (data) => {
    const history = {};
    const checkData = {};
    const suggest_value = {
      "1.1.2": 365,
      "1.1.3": 1,
      "1.1.4": 14,
      "1.2.1": 15,
      "1.2.2": 5,
      "1.2.3": 15,
      "2.3.1.5": "Admin_ash",
      "2.3.1.6": "Guest_ash",
      "2.3.6.5": 30,
      "2.3.7.3": 900,
      "2.3.7.4":
        "You are accessing a U.S. Government (USG) Information System (IS) that is provided for USG-authorized use only.\nBy using this IS (which includes any device attached to this IS), you consent to the following conditions:\n\n    - The USG routinely intercepts and monitors communications on this IS for purposes including, but not limited to, penetration testing, COMSEC monitoring, network operations and defense, personnel misconduct (PM), law enforcement (LE), and counterintelligence (CI) investigations.\n\n    - At any time, the USG may inspect and seize data stored on this IS.\n\n    - Communications using, or data stored on, this IS are not private, are subject to routine monitoring, interception, and search, and may be disclosed or used for any USG-authorized purpose.\n\n    - This IS includes security measures (e.g., authentication and access controls) to protect USG interests--not for your personal benefit or privacy.\n\n    - Notwithstanding the above, using this IS does not constitute consent to PM, LE or CI investigative searching or monitoring of the content of privileged communications, or work product, related to personal representation or services by attorneys, psychotherapists, or clergy, and their assistants. Such communications and work product are private and confidential. See User Agreement for details.",
      "2.3.7.5": "DoD Notice and Consent Banner",
      "2.3.7.7": 14,
      "2.3.9.1": 15,
    };
    for (const d in data) {
      history[d] = true;
      checkData[d] = true;
      if (suggest_value[d.replace("rule_", "").replace(/_/g, ".")] != null) {
        checkData[d] = suggest_value[d.replace("rule_", "").replace(/_/g, ".")];
      }
    }
    setHistory(history);
    setCheckData(checkData);
    localStorage.setItem(serverId, JSON.stringify(checkData));
    localStorage.setItem(`${serverId}-history`, JSON.stringify(history));
  };
  function renderHardening() {
    endOfMessageRef.current = null;
    const rawResult = result_hardening.current;
    let dom1 = [];
    let dom2 = [];
    const pattern_success = /TASK \[(.+?)\].*?\n(.+?): /gi;
    const matches = Array.from(rawResult.matchAll(pattern_success));
    const pattern_failure =
      /TASK \[(.+?)\].*?\nfatal: .*?(UNREACHABLE|FAILED)! => ({\"changed\": .*?, \"msg\": \"(.+?)\", .*?}|{\"msg\": \"(.+?)\"})/gi;
    const matches_failed = Array.from(rawResult.matchAll(pattern_failure));
    // console.log(matches_failed);
    for (const match of matches_failed) {
      dom2.push(
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
            id={match[1]}
            title={
              <div className="flex items-center gap-5">
                <p>
                  {match[1]} {""}
                  <CancelIcon sx={{ color: "red" }} />
                </p>
              </div>
            }
          >
            <p className="content-detail whitespace-pre-wrap">
              <span className="font-bold">Detail:</span> {match[3]}
            </p>
          </AccordionItem>
        </Accordion>
      );
    }

    for (const match of matches) {
      if (match[2] != "skipping" && match[2] != "fatal") {
        // console.log(`${match[1]}: ${match[2]}`);
        dom1.push(
          <Card className="content-card-noneCheckBox" key={match[1]}>
            <CardBody>
              <p className="SubText">
                {match[1]} <CheckCircleIcon color="success" />
              </p>
            </CardBody>
          </Card>
        );
      }
    }
    result_hardening_history.current = dom1;
    result_hardening_history_failed.current = dom2;
  }
  function renderAutoSuggestion(data) {
    endOfMessageRef.current = null;
    let dom = [];
    for (const d in data) {
      if (data[d]["status"] === false) {
        dom.push(
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
              id={d}
              title={
                <div className="flex items-center">
                  {d.replace("rule_", "").replace(/_/g, ".")} {data[d]["name"]}
                </div>
              }
              startContent={
                <Button className="bg-[#2E2E48 w-fit">
                  <DeleteIcon
                    sx={{ color: "red" }}
                    className="cursor-pointer"
                    onClick={() => {
                      delete data[d];
                      autoSuggestionData.current = data;
                      renderAutoSuggestion(data);
                    }}
                  />
                </Button>
              }
            >
              <p className="content-detail whitespace-pre-wrap">
                <span className="font-bold">Value:</span> {data[d]["value"]}
              </p>
            </AccordionItem>
          </Accordion>
        );
      }
    }
    setMessage(dom);
  }
  return (
    <Card className="CardAudit">
      <CardBody className="CardBody">
        <div className="Container">
          <div className="SideBar-Container">
            <SideBar serverId={serverId} />
          </div>
          <div className="Heading-Container">
            <HardenTopper
              changeTopic={changeTopic}
              topic={topic}
              setTopic={setTopic}
              setIsPressHarden={setIsPressHarden}
              serverId={serverId}
              isPressHarden={isPressHarden}
              checkData={checkData}
              setIsPressSuggestion={setIsPressSuggestion}
              IsPressSuggestion={isPressSuggestion}
            />
          </div>
          <div className="Content-Container example">
            <HardenContent
              setChangeTopic={setChangeTopic}
              topic={topic}
              setTopic={setTopic}
              newData={newData}
              checkData={checkData}
              setCheckData={setCheckData}
              serverId={serverId}
              onOpen={onOpen}
              run={run}
              setRun={setRun}
              history={history}
              setHistory={setHistory}
            />
          </div>
          <Modal
            isOpen={modalOneVisible}
            isDismissable={false}
            scrollBehavior="inside"
            size="5xl"
            onClose={() => {
              setModalOneVisible(false);
            }}
          >
            <ModalContent>
              {(onClose) => (
                <>
                  <ModalHeader className="flex flex-col gap-3">
                    Result of Hardening
                  </ModalHeader>
                  <ModalBody className="px-[8rem] bg-[#27273D]">
                    {message != "" ? "" : <Spinner color="white" />}
                    {!run_hardening_success.current ? (
                      <p className="whitespace-pre-wrap text-left text-white">
                        {message}
                        <div ref={endOfMessageRef} />
                      </p>
                    ) : (
                      <p className="whitespace-pre-wrap text-left text-white">
                        {result_hardening_history.current.length > 0 && (
                          <>
                            <p className="font-bold">Success:</p>
                            {result_hardening_history.current}
                          </>
                        )}
                        {result_hardening_history_failed.current.length > 0 && (
                          <>
                            <p className="font-bold">Failed:</p>
                            {result_hardening_history_failed.current}
                          </>
                        )}
                      </p>
                    )}
                  </ModalBody>
                  <ModalFooter>
                    <Button
                      color="danger"
                      onPress={() => {
                        setModalOneVisible(false);
                        window.history.go(0);
                      }}
                    >
                      Close
                    </Button>
                  </ModalFooter>
                </>
              )}
            </ModalContent>
          </Modal>
          <Modal
            isOpen={modalTwoVisible}
            isDismissable={false}
            scrollBehavior="inside"
            size="5xl"
            onClose={() => {
              setModalTwoVisible(false);
            }}
          >
            <ModalContent>
              {(onClose) => (
                <>
                  <ModalHeader className="flex flex-col gap-3">
                    Auto Suggestion
                  </ModalHeader>
                  <ModalBody className="px-[8rem] bg-[#27273D]">
                    {message != "" ? "" : <Spinner color="white" />}
                    <p className="whitespace-pre-wrap text-left text-white">
                      {message}
                      <div ref={endOfMessageRef} />
                    </p>
                  </ModalBody>
                  <ModalFooter>
                    <Button
                      color="primary"
                      onPress={() => {
                        handleSuggestion(autoSuggestionData.current);
                        setModalTwoVisible(false);
                      }}
                    >
                      Confirm
                    </Button>
                    <Button
                      color="danger"
                      onPress={() => {
                        setModalTwoVisible(false);
                        setMessage([]);
                      }}
                    >
                      Close
                    </Button>
                  </ModalFooter>
                </>
              )}
            </ModalContent>
          </Modal>
        </div>
      </CardBody>
    </Card>
  );
}

export default AuditCard;
