import Layout from "../components/Layout";
import SystemTelemetry from "../components/SystemTelemetry";
import ReflexResearchViewer from "../components/ReflexResearchViewer";
import ContextLedgerVisualizer from "../components/ContextLedgerVisualizer";
import AICoreControl from "../components/AICoreControl";

export default function Home() {
  return (
    <Layout>
      <SystemTelemetry />
      <ReflexResearchViewer />
      <ContextLedgerVisualizer />
      <AICoreControl />
    </Layout>
  );
}
