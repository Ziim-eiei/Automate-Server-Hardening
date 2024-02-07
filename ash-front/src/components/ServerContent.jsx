import React, { useRef } from "react";
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

export default function ServerContent() {
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
  const renderCell = React.useCallback((item, columnKey) => {
    const cellValue = item[columnKey];
    // console.log(`${columnKey}: ${cellValue}`);
    switch (columnKey) {
      case "server_ip":
        return (
          <div className="flex flex-col">
            <p
              className="text-bold text-sm select-none text-black underline cursor-pointer w-fit"
              onClick={() => {
                navigate(`/hardening/${item._id}`);
              }}
            >
              <StorageIcon />
              {cellValue}
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
      {data?.server?.length ? (
        <div>
          {/* <p>Project name: {data?.project_name}</p> */}
          <MyButton
            onClick={() => {
              navigate(`/create/server/${projectId}`);
            }}
          >
            Create server
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
          items={data?.server ? data.server : []}
          emptyContent={
            <div>
              <p>Don't have data</p>
              <MyButton
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
      <Modal isOpen={isOpen} onOpenChange={onOpenChange} isDismissable={false}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Delete Server
              </ModalHeader>
              <ModalBody>
                <p>Are you sure to delete this server?</p>
              </ModalBody>
              <ModalFooter>
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
