import _ from 'lodash';
import React from 'react';

import {Timestamp} from '../../../../../Timestamp';
import {parseRefMaybe, SmallRef} from '../../../Browse2/SmallRef';
import {CategoryChip} from '../common/CategoryChip';
import {SimpleKeyValueTable} from '../common/SimplePageLayout';
import {StatusChip} from '../common/StatusChip';
import {GroupedCalls} from '../ObjectVersionPage';
import {WFCall} from '../wfInterface/types';
import {useCalls} from '../wfReactInterface/interface';

export const CallOverview: React.FC<{
  wfCall: WFCall;
}> = ({wfCall}) => {
  const call = wfCall.rawCallSpan();
  const opCategory = wfCall.opVersion()?.opCategory();
  const childCalls = useCalls(wfCall.entity(), wfCall.project(), {
    parentIds: [wfCall.callID()],
  });
  const attributes = _.fromPairs(
    Object.entries(call.attributes ?? {}).filter(
      ([k, a]) => !k.startsWith('_') && a != null
    )
  );
  const summary = _.fromPairs(
    Object.entries(call.summary ?? {}).filter(
      ([k, a]) => !k.startsWith('_') && k !== 'latency_s' && a != null
    )
  );

  return (
    <SimpleKeyValueTable
      data={{
        Operation:
          parseRefMaybe(call.name) != null ? (
            <SmallRef objRef={parseRefMaybe(call.name)!} wfTable="OpVersion" />
          ) : (
            call.name
          ),
        ...(opCategory
          ? {
              Category: <CategoryChip value={opCategory} />,
            }
          : {}),
        Status: <StatusChip value={call.status_code} />,
        Called: <Timestamp value={call.timestamp / 1000} format="relative" />,
        ...(call.summary.latency_s != null
          ? {
              Latency: call.summary.latency_s.toFixed(3) + 's',
            }
          : {}),
        ...(call.exception ? {Exception: call.exception} : {}),
        ...((childCalls.result?.length ?? 0) > 0
          ? {
              'Child Calls': (
                <GroupedCalls
                  calls={childCalls.result!}
                  partialFilter={{
                    parentId: wfCall.callID(),
                  }}
                />
              ),
            }
          : {}),
        ...(Object.keys(attributes).length > 0 ? {Attributes: attributes} : {}),
        ...(Object.keys(summary).length > 0 ? {Summary: summary} : {}),
      }}
    />
  );
};
