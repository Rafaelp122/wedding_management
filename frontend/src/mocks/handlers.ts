import { getAuthMock } from "@/api/generated/v1/endpoints/auth/auth.msw";
import { getDashboardMock } from "@/api/generated/v1/endpoints/dashboard/dashboard.msw";
import { getFinancesMock } from "@/api/generated/v1/endpoints/finances/finances.msw";
import { getLogisticsMock } from "@/api/generated/v1/endpoints/logistics/logistics.msw";
import { getNotificationsMock } from "@/api/generated/v1/endpoints/notifications/notifications.msw";
import { getSchedulerMock } from "@/api/generated/v1/endpoints/scheduler/scheduler.msw";
import { getWeddingsMock } from "@/api/generated/v1/endpoints/weddings/weddings.msw";

export const handlers = [
  ...getAuthMock(),
  ...getDashboardMock(),
  ...getFinancesMock(),
  ...getLogisticsMock(),
  ...getNotificationsMock(),
  ...getSchedulerMock(),
  ...getWeddingsMock(),
];
