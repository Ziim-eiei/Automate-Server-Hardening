const data = [{"id":1,"num":"1"},{"id":2,"num":"2"},{"id":3,"num":"3"}]
export default function Home() {
    return <>
     <h1>Test Home</h1>
     <h1 className="text-3xl font-bold underline">
      Hello world!
    </h1>
    <div>
      {data.map((d)=>{
        return (
          <li key={d.id}>
            num: {d.num}
          </li>
        )
      })}
    </div>
    </>
  }
  