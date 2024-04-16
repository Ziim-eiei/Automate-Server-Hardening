import React, { useRef, useState, useEffect } from "react";
import useSWR, { mutate } from "swr";
import { useNavigate, useParams } from "react-router-dom";
import { EditIcon } from "../components/icons/EditIcon.jsx";
import { DeleteIcon } from "../components/icons/DeleteIcon";
import { MyButton } from "../components/Button";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Tooltip,
  dataFocusVisibleClasses,
} from "@nextui-org/react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
} from "@nextui-org/react";
import StorageIcon from "@mui/icons-material/Storage";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { Spinner } from "@nextui-org/react";
import WarningIcon from "@mui/icons-material/Warning";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import { Card, CardBody } from "@nextui-org/react";

export default function ServerContent() {
  const result_hardening = useRef(null);
  const result_hardening_history = useRef([]);
  const result_hardening_history_failed = useRef([]);
  const run_hardening_success = useRef(false);
  let { projectId } = useParams();
  const navigate = useNavigate();
  const fetcher = (...args) => fetch(...args).then((res) => res.json());
  const { data } = useSWR(
    `http://localhost:8000/api/projects/${projectId}`,
    fetcher
  );
  // console.log(data);
  const server_id = useRef(null);
  const columns = [
    { name: "IP", uid: "server_ip" },
    { name: "USERNAME", uid: "server_username" },
    { name: "PASSWORD", uid: "server_password" },
    { name: "ACTION", uid: "actions" },
  ];
  async function deleteServer(id) {
    await fetch(`http://localhost:8000/api/servers/${id}`, {
      method: "DELETE",
    }).then((res) => res.json());
  }
  const ws = useRef(null);
  const run_history = useRef(null);
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/api/ws");
    ws.current = socket;
    ws.current.onmessage = (e) => {
      setMessage((prev) => [...prev, e.data]);
      run_history.current += e.data;
      if (run_history.current.includes("PLAY [Run Hardening Task]")) {
        result_hardening.current += e.data;
        if (result_hardening.current.includes("PLAY RECAP")) {
          renderHardening();
          run_hardening_success.current = true;
        }
      }
    };
    return () => {
      ws.current.close();
    };
  }, []);
  const [message, setMessage] = useState([]);
  const endOfMessageRef = useRef(null);
  useEffect(() => {
    endOfMessageRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [message?.length]);
  async function runHarden(server_id) {
    if (ws.current.readyState === 1) {
      const run = await fetch("http://localhost:8000/api/auto-hardening", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          server_id: server_id,
        }),
      }).then((res) => res.json());
    }
  }
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
    if (dom1.length == 0 && dom2.length == 0) {
      run_hardening_success.current = true;
      dom1.push(
        <div className="text-white">
          <CheckCircleIcon color="success" /> All topic are passed
        </div>
      );
    }
  }
  const renderCell = React.useCallback((item, columnKey) => {
    const cellValue = item[columnKey];
    // console.log(`${columnKey}: ${cellValue}`);
    switch (columnKey) {
      case "server_ip":
        return (
          <div className="flex flex-col">
            <p
              className="text-bold text-sm select-none text-black cursor-pointer w-fit flex items-center"
              onClick={() => {
                navigate(`/hardening/${item._id}`);
              }}
            >
              <StorageIcon /> &nbsp; {cellValue}
            </p>
          </div>
        );
      case "server_username":
        return (
          <div className="flex flex-col">
            <p className="text-bold text-sm select-none text-black">
              {cellValue}
            </p>
          </div>
        );
      case "server_password":
        return (
          <div className="flex flex-col">
            <p className="text-bold text-sm select-none text-black">
              {cellValue}
            </p>
          </div>
        );
      case "actions":
        return (
          <div className="relative flex items-center gap-5">
            <Tooltip
              content={<span className="text-white">Automate Hardening</span>}
              color="success"
            >
              <span className="text-lg text-success-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    setModalConfirmVisible(true);
                    server_id.current = item._id;
                  }}
                >
                  <PlayArrowIcon color="success" />
                </div>
              </span>
            </Tooltip>

            <Tooltip
              content={<span className="text-white">Edit Server</span>}
              color="warning"
            >
              <span className="text-lg text-warning-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    navigate(`/edit/server/${item._id}`);
                  }}
                >
                  <EditIcon />
                </div>
              </span>
            </Tooltip>
            <Tooltip color="danger" content="Delete Server">
              <span className="text-lg text-danger-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    setModalVisible(true);
                    server_id.current = item._id;
                  }}
                >
                  <DeleteIcon />
                </div>
              </span>
            </Tooltip>
          </div>
        );
      default:
        return cellValue;
    }
  }, []);
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTwoVisible, setModalTwoVisible] = useState(false);
  const [modalConfirmVisible, setModalConfirmVisible] = useState(false);
  return (
    <div style={{ margin: "0px 50px" }}>
      <div className="absolute" style={{ top: 115 }}>
        <p>Project Description: {data?.project_description}</p>
      </div>

      <Table
        aria-label="Example table with custom cells"
        selectionMode="single"
        color={"primary"}
        classNames={{
          base: "max-h-[520px] scroll",
        }}
        isHeaderSticky
      >
        <TableHeader columns={columns}>
          {(column) => (
            <TableColumn
              key={column.uid}
              align={column.uid === "actions" ? "center" : "start"}
              className="select-none"
              style={{ backgroundColor: "#e9e9e9" }}
            >
              {column.name}
            </TableColumn>
          )}
        </TableHeader>
        <TableBody
          items={data?.server ? data.server : []}
          emptyContent={
            <div>
              <p>Don't have a server.</p>
              <MyButton
                className=" bg-[#4A3AFF] text-[#FFFFFF] p-4 mt-2 shadow-xl "
                onClick={() => {
                  navigate(`/create/server/${projectId}`);
                }}
              >
                Create server
              </MyButton>
            </div>
          }
        >
          {(item) => (
            <TableRow key={item._id}>
              {(columnKey) => (
                <TableCell>{renderCell(item, columnKey)}</TableCell>
              )}
            </TableRow>
          )}
        </TableBody>
      </Table>

      <br />

      {data?.server?.length ? (
        <div className="flex justify-center">
          <MyButton
            className=" bg-[#4A3AFF] text-[#FFFFFF] shadow-xl py-5 px-10 rounded-xl "
            onClick={() => {
              navigate(`/create/server/${projectId}`);
            }}
          >
            Create server
          </MyButton>
        </div>
      ) : null}

      <Modal
        isOpen={modalVisible}
        onClose={() => {
          setModalVisible(false);
        }}
        isDismissable={false}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1 border-b-2 mx-8">
                Delete Server
              </ModalHeader>
              <ModalBody>
                <p>Are you sure to delete this server?</p>
              </ModalBody>
              <ModalFooter>
                <Button
                  color="primary"
                  onPress={() => {
                    onClose();
                  }}
                >
                  No
                </Button>
                <Button
                  color="danger"
                  onPress={() => {
                    deleteServer(server_id.current);
                    mutate(
                      `http://localhost:8000/api/projects/${projectId}`,
                      async (data) => {
                        return {
                          ...data,
                          server: data.server.filter(
                            (item) => item._id !== server_id.current
                          ),
                        };
                      },
                      { revalidate: true }
                    );
                    onClose();
                  }}
                >
                  Yes
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
                Result of Automate Hardening
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
                    setModalTwoVisible(false);
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
        isOpen={modalConfirmVisible}
        isDismissable={false}
        size="2xl"
        onClose={() => {
          setModalConfirmVisible(false);
        }}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-3">
                <span>
                  <WarningIcon sx={{ color: "orange" }} /> Warning
                </span>
              </ModalHeader>
              <ModalBody className="px-[2rem]">
                <p>
                  This action will run the automate hardening process on the
                  server. (It means you can't select any topics.){" "}
                  <p className="font-bold">Are you sure to continue?</p>
                </p>
              </ModalBody>
              <ModalFooter>
                <Button
                  color="danger"
                  onPress={() => {
                    setModalConfirmVisible(false);
                  }}
                >
                  No
                </Button>
                <Button
                  color="primary"
                  onPress={() => {
                    setModalConfirmVisible(false);
                    setModalTwoVisible(true);
                    runHarden(server_id.current);
                  }}
                >
                  Yes
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </div>
  );
}
