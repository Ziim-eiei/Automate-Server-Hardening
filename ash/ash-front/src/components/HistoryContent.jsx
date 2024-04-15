import React, { useRef, useState } from "react";
import useSWR, { mutate } from "swr";
import { useNavigate, useParams } from "react-router-dom";
import { EditIcon } from "../components/icons/EditIcon.jsx";
import { DeleteIcon } from "../components/icons/DeleteIcon";
import StorageIcon from "@mui/icons-material/Storage";
import { Card, CardBody } from "@nextui-org/react";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import "../css/Card.css";
import { Accordion, AccordionItem } from "@nextui-org/react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Tooltip,
  Chip,
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

export default function HistoryContent() {
  //   let { projectId } = useParams();
  const navigate = useNavigate();
  const fetcher = (...args) => fetch(...args).then((res) => res.json());
  const { data } = useSWR(`http://localhost:8000/api/hardening`, fetcher);
  //   console.log(data);
  //   const server_id = useRef(null);
  const columns = [
    { name: "IP", uid: "name" },
    { name: "RUN AT", uid: "run_at" },
    { name: "STATUS", uid: "status" },
  ];
  const result_history = useRef(null);
  const result_history_failed = useRef(null);
  const result_history_original = useRef(null);
  const time = useRef(null);
  function renderResult(rawResult) {
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
    result_history.current = dom1;
    result_history_failed.current = dom2;
  }
  const renderCell = React.useCallback((item, columnKey) => {
    const cellValue = item[columnKey];
    // console.log(`${columnKey}: ${cellValue}`);
    switch (columnKey) {
      case "name":
        return (
          <div className="flex flex-col">
            <p
              className="text-bold text-sm select-none text-black cursor-pointer w-fit  flex items-center"
              onClick={() => {
                onOpen();
                renderResult(item["history"]);
                result_history_original.current = item["history"];
              }}
            >
              <StorageIcon /> &nbsp; {cellValue}
            </p>
          </div>
        );
      case "run_at":
        const utcDateString = cellValue;
        const utcDateWithoutMillis = utcDateString.slice(0, -5) + "Z";
        const utcDate = new Date(utcDateWithoutMillis);
        const offsetMinutes = utcDate.getTimezoneOffset();
        const localTime = new Date(
          utcDate.getTime() - offsetMinutes * 60 * 1000
        );
        const utc_format = localTime
          .toISOString()
          .slice(0, -5)
          .replace("T", " ")
          .replace("-", "/")
          .replace("-", "/");
        let date = utc_format.split(" ")[0];
        date = date.split("/").reverse().join("/");
        time.current = date + " " + utc_format.split(" ")[1];
        return (
          <div className="flex flex-col">
            <p className="text-bold text-sm select-none text-black">
              {time?.current}
            </p>
          </div>
        );
      case "status":
        return cellValue === "success" ? (
          <Chip
            className="select-none"
            color="success"
            size="sm"
            variant="flat"
          >
            {cellValue}
          </Chip>
        ) : (
          <Chip className="select-none" color="danger" size="sm" variant="flat">
            {cellValue}
          </Chip>
        );
      case "actions":
        return (
          <div className="relative flex items-center gap-5">
            <Tooltip content="Edit server" color="warning">
              <span className="text-lg text-warning-400 cursor-pointer active:opacity-50">
                <EditIcon />
              </span>
            </Tooltip>
            <Tooltip color="danger" content="Delete server">
              <span className="text-lg text-danger-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    onOpen();
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
  return (
    <div style={{ margin: "0px 50px" }}>
      <Table
        aria-label="Example table with custom cells"
        selectionMode="single"
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
          items={data ? data : []}
          emptyContent={
            <div>
              {/* <p>Don't have data</p> */}
              <p>Don't have a history.</p>
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
      <Modal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        scrollBehavior="inside"
        size="5xl"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Result of Hardening
              </ModalHeader>
              <ModalBody className="px-[8rem] bg-[#27273D]">
                <div className="whitespace-pre-wrap text-left text-white">
                  {result_history.current.length > 0 && (
                    <>
                      <p className="font-bold">Success:</p>
                      {result_history.current}
                    </>
                  )}
                  {result_history_failed.current.length > 0 && (
                    <>
                      <p className="font-bold">Failed:</p>
                      {result_history_failed.current}
                    </>
                  )}
                </div>
              </ModalBody>
              <ModalFooter>
                <Button
                  color="danger"
                  onPress={() => {
                    onClose();
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
  );
}
