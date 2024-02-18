import React, { useRef, useState } from "react";
import useSWR, { mutate } from "swr";
import { useNavigate } from "react-router-dom";
import { MyButton } from "../components/Button";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Tooltip,
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
import { EditIcon } from "../components/icons/EditIcon.jsx";
import { DeleteIcon } from "../components/icons/DeleteIcon";
import { EyeIcon } from "../components/icons/EyeIcon";
import FolderIcon from "@mui/icons-material/Folder";

const columns = [
  { name: "PROJECT NAME", uid: "project_name" },
  { name: "CREATE AT", uid: "created_at" },
  { name: "SERVER AMOUNT", uid: "server" },
  { name: "ACTIONS", uid: "actions" },
];
export default function ProjectContent() {
  const navigate = useNavigate();
  const fetcher = (...args) => fetch(...args).then((res) => res.json());
  const { data } = useSWR("http://localhost:8000/api/projects", fetcher);
  const deleteProject = async (id) => {
    await fetch(`http://localhost:8000/api/projects/${id}`, {
      method: "DELETE",
    }).then((res) => res.json());
  };
  const project_id = useRef(null);
  const time = useRef(null);
  const renderCell = React.useCallback((item, columnKey) => {
    const cellValue = item[columnKey];
    // console.log(`${columnKey}: ${cellValue}`);
    switch (columnKey) {
      case "project_name":
        return (
          <div className="">
            <p
              className="text-bold text-sm select-none text-black underline cursor-pointer w-fit"
              onClick={() => {
                navigate(`/server/${item._id}`);
              }}
            >
              <FolderIcon />
              {cellValue}
            </p>
          </div>
        );
      case "created_at":
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
          <div className="">
            <p className="text-bold text-sm select-none text-black">
              {time?.current}
            </p>
          </div>
        );
      case "server":
        return (
          <Chip
            className="select-none"
            color={"success"}
            size="sm"
            variant="flat"
          >
            {cellValue.length}
          </Chip>
        );
      case "actions":
        return (
          <div className="relative flex items-center gap-5">
            <Tooltip content="Details" color="primary">
              <span className="text-lg text-primary-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    navigate(`/server/${item._id}`);
                  }}
                >
                  <EyeIcon />
                </div>
              </span>
            </Tooltip>
            <Tooltip content="Edit project" color="warning">
              <span className="text-lg text-warning-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    navigate(`/edit/project/${item._id}`);
                  }}
                >
                  <EditIcon />
                </div>
              </span>
            </Tooltip>
            <Tooltip color="danger" content="Delete project">
              <span className="text-lg text-danger-400 cursor-pointer active:opacity-50">
                <div
                  onClick={() => {
                    onOpen();
                    project_id.current = item._id;
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
      {data?.length ? (
        <div>
          <MyButton
            onClick={() => {
              navigate("/create/project");
            }}
          >
            Create project
          </MyButton>
          <br />
          <br />
        </div>
      ) : null}

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
              <MyButton
                onClick={() => {
                  navigate("/create/project");
                }}
              >
                Create project
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
      <Modal isOpen={isOpen} onOpenChange={onOpenChange} isDismissable={false}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Delete Project
              </ModalHeader>
              <ModalBody>
                <p>Are you sure to delete this project?</p>
              </ModalBody>
              <ModalFooter>
                <Button
                  color="danger"
                  onPress={() => {
                    deleteProject(project_id.current);
                    mutate(
                      "http://localhost:8000/api/projects",
                      async (data) => {
                        return data.filter(
                          (project) => project._id !== project_id.current
                        );
                      },
                      { revalidate: true }
                    );
                    onClose();
                  }}
                >
                  Yes
                </Button>
                <Button
                  color="primary"
                  onPress={() => {
                    onClose();
                  }}
                >
                  No
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </div>
  );
}
