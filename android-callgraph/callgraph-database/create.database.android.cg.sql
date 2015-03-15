--CREATE TABLE "nodes" (
--    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
--    "call" TEXT NOT NULL
--)
--
--CREATE TABLE "edges" (
--    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
--    "callee" INTEGER NOT NULL,
--    "caller" INTEGER NOT NULL
--);
--
--CREATE UNIQUE INDEX "uk_call" on nodes (call ASC)

-- Describe EDGES
CREATE TABLE edges (
    "id" INTEGER PRIMARY KEY,
    "caller" TEXT NOT NULL,
    "caller_package" TEXT NOT NULL,
    "callee" TEXT NOT NULL,
    "callee_package" TEXT NOT NULL,
    "app" TEXT NOT NULL
);

