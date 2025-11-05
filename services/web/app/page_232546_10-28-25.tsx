"use client";
import { motion } from "framer-motion";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@radix-ui/react-tabs";

export default function Home() {
  return (
    <motion.div
      className="flex flex-col items-center justify-center h-full text-center px-6"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1.2 }}
    >
      <h1 className="text-5xl font-mono text-gold mb-6 tracking-wide">savant</h1>
      <p className="max-w-lg text-sm text-gold-light/80 leading-relaxed mb-10">
        The baseline UI template — modular, adaptive, fractal.  
        Built for intelligence, precision, and the golden ratio of interface design.
      </p>
      <Tabs defaultValue="overview">
        <TabsList className="flex gap-4 justify-center mb-8">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="components">Components</TabsTrigger>
          <TabsTrigger value="animation">Motion</TabsTrigger>
        </TabsList>
        <TabsContent value="overview">
          <div className="p-6 border border-gold-dark rounded-lg">
            <p>Every Savant interface begins as a lattice of shards —  
            self-similar modules that grow complexity through hierarchy.</p>
          </div>
        </TabsContent>
        <TabsContent value="components">
          <div className="p-6 border border-gold-dark rounded-lg">
            <p>Core components follow a strict fractal structure:  
            Panels → Facets → Lattices → Shards → Filaments.</p>
          </div>
        </TabsContent>
        <TabsContent value="animation">
          <motion.div
            className="p-6 border border-gold-dark rounded-lg"
            whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(200,167,64,0.35)" }}
          >
            <p>Framer Motion ensures subtle kinetic feedback —  
            never gratuitous, always precise.</p>
          </motion.div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
