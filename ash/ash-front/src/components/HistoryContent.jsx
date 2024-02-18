import React, { useRef, useState } from "react";
import useSWR, { mutate } from "swr";
import { useNavigate, useParams } from "react-router-dom";
import { EditIcon } from "../components/icons/EditIcon.jsx";
import { DeleteIcon } from "../components/icons/DeleteIcon";
import { MyButton } from "../components/Button";
import StorageIcon from "@mui/icons-material/Storage";
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
  const time = useRef(null);
  const renderCell = React.useCallback((item, columnKey) => {
    const cellValue = item[columnKey];
    // console.log(`${columnKey}: ${cellValue}`);
    switch (columnKey) {
      case "name":
        return (
          <div className="flex flex-col">
            <p
              className="text-bold text-sm select-none text-black underline cursor-pointer w-fit"
              onClick={() => {
                onOpen();
                result_history.current = item["history"];
              }}
            >
              <StorageIcon />
              {cellValue}
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
    <div className="p-5">
      <Table
        aria-label="Example table with custom cells"
        selectionMode="single"
        color={"primary"}
      >
        <TableHeader columns={columns}>
          {(column) => (
            <TableColumn
              key={column.uid}
              align={column.uid === "actions" ? "center" : "start"}
              className="select-none"
            >
              {column.name}
            </TableColumn>
          )}
        </TableHeader>
        <TableBody
          items={data ? data : []}
          emptyContent={
            <div>
              <p>Don't have data</p>
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
                Result of server
              </ModalHeader>
              <ModalBody>
                <p className="whitespace-pre-wrap text-left text-black">
                  {result_history.current}
                </p>
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
