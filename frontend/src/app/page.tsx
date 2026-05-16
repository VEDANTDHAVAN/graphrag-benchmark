import {
  AccuracySection,
  ArchitectureSection,
  DatasetSection,
  DeploymentSection,
  MethodologySection,
  TechStackSection,
  TigerGraphPivotSection,
  WhyGraphRAGSection,
} from "./components/showcase/InfoSections";
import { FooterSection } from "./components/showcase/FooterSection";
import { HeroSection } from "./components/showcase/HeroSection";
import { ResultsSection } from "./components/showcase/ResultsSection";
import { ShowcaseNav } from "./components/showcase/ShowcaseNav";
import { getFinalSummary } from "./lib/showcase";

export const dynamic = "force-dynamic";

export default async function Home() {
  const { summary, source } = await getFinalSummary();

  return (
    <main>
      <HeroSection />
      <ShowcaseNav />
      <WhyGraphRAGSection />
      <DatasetSection />
      <MethodologySection />
      <AccuracySection />
      <ArchitectureSection />
      <TechStackSection />
      <TigerGraphPivotSection />
      <ResultsSection summary={summary} source={source} />
      <DeploymentSection />
      <FooterSection />
    </main>
  );
}
