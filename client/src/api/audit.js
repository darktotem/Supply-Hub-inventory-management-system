import { api } from "./client";

export const verifyAuditChain = () => api("/audits/verify");
