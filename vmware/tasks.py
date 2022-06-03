from celery import shared_task

from vmware.workers.PollWorker import PollWorker

@shared_task(name="pollVmware_task")
def pollVmwareAsync_task(assetId, taskMoId, targetId, guestSpec, forceDisableSecondStage):
    return PollWorker(assetId, taskMoId, targetId, guestSpec, forceDisableSecondStage)()
