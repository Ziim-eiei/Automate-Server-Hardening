import React from 'react'
import useSWR from 'swr'
import { MyInput } from "./Input";

function HardenContent() {
    const fetcher = (...args) => fetch(...args).then(res => res.json())
    const { data, error, isLoading } = useSWR('http://localhost:8000/api/documents', fetcher)
    return (

        <div className="text-white" style={{ whiteSpace: "pre-wrap", textAlign: "left" }}>
            {data?.map((item) => {
                return (
                    <li key={item._id} className='content-box'>
                        no: {item.benchmark_no} <br />
                        topic: {item.benchmark_name} <br />
                        child: {item.benchmark_child?.map((item2) => {
                            return item2.benchmark_child?.map(item3 => {
                                return <li key={item3.benchmark_no}>{item3.benchmark_no}</li>
                            })
                        })}
                    </li>
                )
            })}
        </div>
    )
}

export default HardenContent