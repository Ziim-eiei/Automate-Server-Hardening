import { MyInput } from "../components/Input"
import { SearchIcon } from "../components/SearchIcon"
import { useState } from "react"

export default function Test() {
  const [inputValue, setInputValue] = useState('');
  const handleClear = () => {
    setInputValue('');
  };
    return <>
     <h1 className="text-white">Test page</h1>
     <div className="">
     <MyInput
      isClearable
      placeholder="Search yout topic"
      radius="full"
      startContent={<SearchIcon/>}
      value={inputValue}
      onChange={(event) => setInputValue(event.target.value)}
      onClear={handleClear}
      color="warning"
    />
    </div>
    </>
  }