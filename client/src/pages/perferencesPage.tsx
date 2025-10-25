"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Progress } from "@/components/ui/progress";
import { Check } from "lucide-react";

// --- Sample Data ---
const genres = [
  {
    name: "Action",
    img: "https://images.unsplash.com/photo-1608889175123-8d8a6b5cb501?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Comedy",
    img: "https://images.unsplash.com/photo-1525182008055-f88b95ff7980?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Drama",
    img: "https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Horror",
    img: "https://images.unsplash.com/photo-1504274066651-8d31a536b11a?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Romance",
    img: "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Sci-Fi",
    img: "https://images.unsplash.com/photo-1504805572947-34fad45aed93?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Fantasy",
    img: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Thriller",
    img: "https://images.unsplash.com/photo-1505685296765-3a2736de412f?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Animation",
    img: "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Adventure",
    img: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
  },
];

const directors = [
  {
    name: "Christopher Nolan",
    img: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Steven Spielberg",
    img: "https://images.unsplash.com/photo-1502741338009-cac2772e18bc?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Martin Scorsese",
    img: "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Quentin Tarantino",
    img: "https://images.unsplash.com/photo-1504274066651-8d31a536b11a?auto=format&fit=crop&w=800&q=80",
  },
  {
    name: "Denis Villeneuve",
    img: "https://images.unsplash.com/photo-1505685296765-3a2736de412f?auto=format&fit=crop&w=800&q=80",
  },
];

export default function PreferencesPage() {
  const [step, setStep] = useState(1);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedDirectors, setSelectedDirectors] = useState<string[]>([]);

  const totalSteps = 3;
  const progress = (step / totalSteps) * 100;

  const nextStep = () => {
    if (step < totalSteps) setStep((prev) => prev + 1);
    else alert("All preferences saved!");
  };

  const prevStep = () => setStep((prev) => Math.max(1, prev - 1));

  return (
    <div className="flex-1 w-full h-full overflow-hidden box-border p-6 flex items-center justify-center">
      <Card className="w-full max-w-4xl h-full max-h-[720px] flex flex-col">
        {/* Title */}
        <div className="w-full flex items-center justify-center border-b border-border py-4">
          <h2 className="text-lg font-semibold tracking-wide">
            User-Preference
          </h2>
        </div>

        {/* Dynamic Step Header */}
        <CardHeader className="pb-2">
          <CardTitle>
            {step === 1 ? "Genres" : step === 2 ? "Directors" : "Summary"}
          </CardTitle>
          <CardDescription>
            {step === 1
              ? "Select your favorite genres."
              : step === 2
              ? "Choose directors you love."
              : "Review your preferences before continuing."}
          </CardDescription>
        </CardHeader>

        {/* Animated Carousel Content */}
        <CardContent className="flex-1 overflow-auto relative">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div
                key="genres"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.3 }}
              >
                <ToggleGroup
                  type="multiple"
                  value={selectedGenres}
                  onValueChange={setSelectedGenres}
                  className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-5 justify-items-center"
                >
                  {genres.map((genre) => (
                    <ToggleGroupItem
                      key={genre.name}
                      value={genre.name}
                      className="relative overflow-hidden rounded-xl p-0 w-40 h-40 border-2 border-transparent data-[state=on]:border-primary group transition-all flex items-center justify-center cursor-pointer"
                    >
                      <img
                        src={genre.img}
                        alt={genre.name}
                        className="absolute inset-0 w-full h-full object-cover brightness-75 group-hover:brightness-90 transition-all"
                      />
                      <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-all" />
                      <p className="relative z-10 text-white text-sm font-medium">
                        {genre.name}
                      </p>
                      {selectedGenres.includes(genre.name) && (
                        <Check
                          className="absolute top-1 right-1 w-5 h-5 text-white transition-opacity"
                          strokeWidth={3}
                        />
                      )}
                    </ToggleGroupItem>
                  ))}
                </ToggleGroup>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="directors"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <ToggleGroup
                  type="multiple"
                  value={selectedDirectors}
                  onValueChange={setSelectedDirectors}
                  className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-5 justify-items-center"
                >
                  {directors.map((director) => (
                    <ToggleGroupItem
                      key={director.name}
                      value={director.name}
                      onClick={() =>
                        setSelectedDirectors((prev) =>
                          prev.includes(director.name)
                            ? prev.filter((d) => d !== director.name)
                            : [...prev, director.name]
                        )
                      }
                      className="relative overflow-hidden rounded-xl p-0 w-40 h-40 border-2 border-transparent data-[state=on]:border-primary group transition-all flex items-center justify-center cursor-pointer"
                    >
                      <img
                        src={director.img}
                        alt={director.name}
                        className="absolute inset-0 w-full h-full object-cover brightness-75 group-hover:brightness-90 transition-all"
                      />
                      <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-all" />
                      <p className="relative z-10 text-white text-sm font-medium">
                        {director.name}
                      </p>
                      {selectedDirectors.includes(director.name) && (
                        <Check
                          className="absolute top-1 right-1 w-5 h-5 text-white transition-opacity"
                          strokeWidth={3}
                        />
                      )}
                    </ToggleGroupItem>
                  ))}
                </ToggleGroup>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="summary"
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.3 }}
                className="flex flex-col gap-3 text-sm text-muted-foreground"
              >
                <div>
                  <strong>Genres:</strong> {selectedGenres.join(", ") || "None"}
                </div>
                <div>
                  <strong>Directors:</strong>{" "}
                  {selectedDirectors.join(", ") || "None"}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>

        {/* Footer */}
        <CardFooter className="mt-auto flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
          <div className="flex-1 w-full">
            <Progress value={progress} className="w-full h-2" />
          </div>

          <div className="flex gap-2">
            {step > 1 && (
              <Button variant="outline" onClick={prevStep}>
                Back
              </Button>
            )}
            <Button
              disabled={
                (step === 1 && selectedGenres.length < 3) ||
                (step === 2 && selectedDirectors.length < 2)
              }
              onClick={nextStep}
            >
              {step === totalSteps ? "Finish" : "Next"}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
