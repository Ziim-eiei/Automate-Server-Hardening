import { useNavigate } from "react-router-dom";
import { MyButton } from "../components/Button";
export default function Home() {
  const navigate = useNavigate();
  return (
    <>
      <h1 className="text-3xl font-bold underline text-white">Hello world!</h1>
      <h1 className="text-3xl font-bold underline text-white">ฝากทำด้วยครับ</h1>
      <br />
      <MyButton
        onClick={() => {
          navigate("/project");
        }}
      >
        Get Start
      </MyButton>
    </>
  );
}
