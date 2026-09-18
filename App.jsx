import { useEffect, useMemo, useState } from "react";
import Map, { Source, Layer, NavigationControl } from "react-map-gl";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from "chart.js";
import { request, login, register } from "./lib/api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const token = import.meta.env.VITE_MAPBOX_TOKEN;

function Auth({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({name:"",email:"demo@darukaa.earth",password:"DarukaaDemo123!"});
  const [error, setError] = useState("");
  async function submit(e) {
    e.preventDefault(); setError("");
    try {
      if (mode === "register") await register(form.name, form.email, form.password);
      await login(form.email, form.password); onAuth();
    } catch (err) { setError(err.message); }
  }
  return <div className="auth"><div className="auth-card">
    <div className="brand">DARUKAA<span>.EARTH</span></div>
    <h1>{mode === "login" ? "Welcome back" : "Create account"}</h1>
    <p className="muted">Carbon & biodiversity intelligence dashboard</p>
    <form onSubmit={submit}>
      {mode==="register" && <input placeholder="Full name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required/>}
      <input type="email" placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required/>
      <input type="password" placeholder="Password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required/>
      {error && <div className="error">{error}</div>}
      <button>{mode==="login" ? "Sign in" : "Register"}</button>
    </form>
    <button className="link" onClick={()=>setMode(mode==="login"?"register":"login")}>
      {mode==="login" ? "Create an account" : "Back to sign in"}
    </button>
  </div></div>
}

function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("darukaa_token"));
  if (!authed) return <Auth onAuth={()=>setAuthed(true)}/>;
  return <Dashboard onLogout={()=>{localStorage.removeItem("darukaa_token");setAuthed(false)}}/>;
}

function Dashboard({onLogout}) {
  const [projects,setProjects]=useState([]), [selected,setSelected]=useState(null);
  const [sites,setSites]=useState([]), [metrics,setMetrics]=useState([]);
  const [showCreate,setShowCreate]=useState(false), [loading,setLoading]=useState(true);
  const [projectForm,setProjectForm]=useState({name:"",description:""});
  const [siteForm,setSiteForm]=useState({name:"",geojson:null});
  const [view,setView]=useState("map");

  useEffect(()=>{request("/projects").then(d=>{setProjects(d.projects);setLoading(false)}).catch(console.error)},[]);
  useEffect(()=>{request("/sites").then(d=>setSites(d.sites)).catch(console.error)},[]);
  async function selectSite(site) {
    setSelected(site);
    const d=await request(`/sites/${site.id}/metrics`); setMetrics(d.metrics);
    setView("analytics");
  }
  async function createProject(e) {
    e.preventDefault();
    const d=await request("/projects",{method:"POST",body:JSON.stringify(projectForm)});
    setProjects([d.project,...projects]);setProjectForm({name:"",description:""});setShowCreate(false);
  }
  const geojson = useMemo(()=>({type:"FeatureCollection",features:sites.filter(s=>s.geometry).map(s=>({
    type:"Feature",properties:{id:s.id,name:s.name},geometry:s.geometry
  }))}),[sites]);
  const chart = {
    labels: metrics.map(m=>m.observed_on),
    datasets:[
      {label:"Carbon (tCO₂e)",data:metrics.map(m=>m.carbon_tco2e),tension:.35},
      {label:"Biodiversity index",data:metrics.map(m=>m.biodiversity_index),tension:.35},
      {label:"Tree cover %",data:metrics.map(m=>m.tree_cover_pct),tension:.35}
    ]
  };
  return <div className="app">
    <header><div className="brand">DARUKAA<span>.EARTH</span></div><div className="header-actions">
      <button className="ghost" onClick={()=>setShowCreate(true)}>+ New project</button><button className="ghost" onClick={onLogout}>Sign out</button>
    </div></header>
    <main>
      <aside>
        <div className="side-title">PROJECTS</div>
        {loading ? <p className="muted">Loading…</p> : projects.map(p=><button key={p.id} className="project" onClick={()=>setSelected(p)}>
          <strong>{p.name}</strong><small>{p.site_count||0} sites · {p.status}</small>
        </button>)}
      </aside>
      <section className="workspace">
        <div className="toolbar">
          <button className={view==="map"?"active":""} onClick={()=>setView("map")}>Map overview</button>
          <button className={view==="analytics"?"active":""} onClick={()=>setView("analytics")}>Analytics</button>
        </div>
        {view==="map" ? <div className="map-wrap">
          <Map initialViewState={{longitude:78.9629,latitude:20.5937,zoom:4}} mapboxAccessToken={token} mapStyle="mapbox://styles/mapbox/light-v11" interactiveLayerIds={["sites-fill"]} onClick={e=>{
            const f=e.features?.[0]; if(f){const s=sites.find(x=>x.id===f.properties.id); if(s)selectSite(s)}
          }}>
            <NavigationControl position="bottom-right"/>
            <Source id="sites" type="geojson" data={geojson}>
              <Layer id="sites-fill" type="fill" paint={{"fill-opacity":.35}}/>
              <Layer id="sites-line" type="line" paint={{"line-width":2}}/>
            </Source>
          </Map>
          <div className="map-overlay"><strong>{sites.length}</strong><span>geospatial sites</span></div>
        </div> : <Analytics site={selected} metrics={metrics} chart={chart}/>}
      </section>
    </main>
    {showCreate && <div className="modal"><div className="modal-card"><button className="close" onClick={()=>setShowCreate(false)}>×</button>
      <h2>Create project</h2><form onSubmit={createProject}><input placeholder="Project name" required value={projectForm.name} onChange={e=>setProjectForm({...projectForm,name:e.target.value})}/>
      <textarea placeholder="Description" value={projectForm.description} onChange={e=>setProjectForm({...projectForm,description:e.target.value})}/><button>Create project</button></form>
      <p className="muted">After creation, sites can be added through the API using GeoJSON polygons.</p>
    </div></div>}
  </div>
}

function Analytics({site,metrics,chart}) {
  if(!site) return <div className="empty"><h2>Select a site</h2><p>Click a polygon on the map to inspect its performance over time.</p></div>;
  const latest=metrics.at(-1), first=metrics[0];
  const delta=(key)=>latest&&first ? (latest[key]-first[key]).toFixed(2) : "—";
  return <div className="analytics"><div className="analytics-head"><div><span className="eyebrow">SITE ANALYTICS</span><h1>{site.name}</h1><p>{site.project_name} · {site.area_hectares?.toFixed?.(2) || "—"} ha</p></div>
  <span className="pill">{site.status||"active"}</span></div>
  <div className="cards">
    <div><span>Carbon</span><strong>{latest?.carbon_tco2e??"—"}</strong><small>Δ {delta("carbon_tco2e")} tCO₂e</small></div>
    <div><span>Biodiversity</span><strong>{latest?.biodiversity_index??"—"}</strong><small>Δ {delta("biodiversity_index")}</small></div>
    <div><span>Tree cover</span><strong>{latest?.tree_cover_pct??"—"}%</strong><small>Δ {delta("tree_cover_pct")} pp</small></div>
    <div><span>Soil organic carbon</span><strong>{latest?.soil_organic_carbon_pct??"—"}%</strong><small>latest observation</small></div>
  </div>
  <div className="chart-card"><h3>Performance over time</h3><Line data={chart} options={{responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false}}}/></div>
  </div>
}
export default App;
