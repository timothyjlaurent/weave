import React from 'react';
import {Link as LinkComp} from 'react-router-dom';
import styled from 'styled-components';

import {
  MOON_550,
  MOON_700,
  TEAL_500,
  TEAL_600,
} from '../../../../../../common/css/color.styles';
import {TargetBlank} from '../../../../../../common/util/links';
import {useWeaveflowRouteContext} from '../../context';
import {WFHighLevelCallFilter} from '../CallsPage/CallsPage';
import {WFHighLevelObjectVersionFilter} from '../ObjectVersionsPage';
import {WFHighLevelOpVersionFilter} from '../OpVersionsPage';
import {WFHighLevelTypeVersionFilter} from '../TypeVersionsPage';
import {truncateID} from '../util';

type LinkVariant = 'primary' | 'secondary';

type LinkProps = {
  $variant?: LinkVariant;
};

export const Link = styled(LinkComp)<LinkProps>`
  font-weight: 600;
  color: ${p => (p.$variant === 'secondary' ? MOON_700 : TEAL_600)};
  &:hover {
    color: ${p => (p.$variant === 'secondary' ? MOON_550 : TEAL_500)};
  }
`;
Link.displayName = 'S.Link';

export const docUrl = (path: string): string => {
  return 'https://wandb.github.io/weave/' + path;
};

export const DocLink = (props: {path: string; text: string}) => {
  return <TargetBlank href={docUrl(props.path)}>{props.text}</TargetBlank>;
};

export const TypeLink: React.FC<{
  entityName: string;
  projectName: string;
  typeName: string;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  return (
    <Link
      to={peekingRouter.typeUIUrl(
        props.entityName,
        props.projectName,
        props.typeName
      )}>
      {props.typeName}
    </Link>
  );
};

export const TypeVersionLink: React.FC<{
  entityName: string;
  projectName: string;
  typeName: string;
  version: string;
  hideName?: boolean;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  const text = props.hideName
    ? props.version
    : props.typeName + ': ' + truncateID(props.version);
  return (
    <Link
      to={peekingRouter.typeVersionUIUrl(
        props.entityName,
        props.projectName,
        props.typeName,
        props.version
      )}>
      {text}
    </Link>
  );
};

export const ObjectLink: React.FC<{
  entityName: string;
  projectName: string;
  objectName: string;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  return (
    <Link
      to={peekingRouter.objectUIUrl(
        props.entityName,
        props.projectName,
        props.objectName
      )}>
      {props.objectName}
    </Link>
  );
};

export const objectVersionText = (opName: string, versionIndex: number) => {
  let text = opName;
  text += ':v' + versionIndex;
  return text;
};

export const ObjectVersionLink: React.FC<{
  entityName: string;
  projectName: string;
  objectName: string;
  version: string;
  versionIndex: number;
  filePath: string;
  refExtra?: string;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  // const text = props.hideName
  //   ? props.version
  //   : props.objectName + ': ' + truncateID(props.version);
  const text = objectVersionText(props.objectName, props.versionIndex);
  return (
    <Link
      to={peekingRouter.objectVersionUIUrl(
        props.entityName,
        props.projectName,
        props.objectName,
        props.version,
        props.filePath,
        props.refExtra
      )}>
      {text}
    </Link>
  );
};

export const OpLink: React.FC<{
  entityName: string;
  projectName: string;
  opName: string;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  return (
    <Link
      to={peekingRouter.opUIUrl(
        props.entityName,
        props.projectName,
        props.opName
      )}>
      {props.opName}
    </Link>
  );
};

export const opNiceName = (opName: string) => {
  let text = opName;
  if (text.startsWith('op-')) {
    text = text.slice(3);
  }
  return text;
};

export const opVersionText = (opName: string, versionIndex: number) => {
  let text = opNiceName(opName);
  text += ':v' + versionIndex;
  return text;
};

export const OpVersionLink: React.FC<{
  entityName: string;
  projectName: string;
  opName: string;
  version: string;
  versionIndex: number;
  variant?: LinkVariant;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  // const text = props.hideName
  //   ? props.version
  //   : props.opName + ': ' + truncateID(props.version);
  const text = opVersionText(props.opName, props.versionIndex);
  return (
    <Link
      $variant={props.variant}
      to={peekingRouter.opVersionUIUrl(
        props.entityName,
        props.projectName,
        props.opName,
        props.version
      )}>
      {text}
    </Link>
  );
};

export const CallLink: React.FC<{
  entityName: string;
  projectName: string;
  opName: string;
  callId: string;
  variant?: LinkVariant;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  const opName = opNiceName(props.opName);
  const truncatedId = truncateID(props.callId);
  return (
    <Link
      $variant={props.variant}
      to={peekingRouter.callUIUrl(
        props.entityName,
        props.projectName,
        '',
        props.callId
      )}>
      {opName} ({truncatedId})
    </Link>
  );
};

export const CallsLink: React.FC<{
  entity: string;
  project: string;
  callCount: number;
  filter?: WFHighLevelCallFilter;
  neverPeek?: boolean;
  variant?: LinkVariant;
}> = props => {
  const {peekingRouter, baseRouter} = useWeaveflowRouteContext();
  const router = props.neverPeek ? baseRouter : peekingRouter;
  return (
    <Link
      $variant={props.variant}
      to={router.callsUIUrl(props.entity, props.project, props.filter)}>
      {props.callCount} calls
    </Link>
  );
};

export const ObjectVersionsLink: React.FC<{
  entity: string;
  project: string;
  versionCount: number;
  filter?: WFHighLevelObjectVersionFilter;
  neverPeek?: boolean;
  variant?: LinkVariant;
}> = props => {
  const {peekingRouter, baseRouter} = useWeaveflowRouteContext();
  const router = props.neverPeek ? baseRouter : peekingRouter;
  return (
    <Link
      $variant={props.variant}
      to={router.objectVersionsUIUrl(
        props.entity,
        props.project,
        props.filter
      )}>
      {props.versionCount} version{props.versionCount !== 1 ? 's' : ''}
    </Link>
  );
};

export const OpVersionsLink: React.FC<{
  entity: string;
  project: string;
  versionCount: number;
  filter?: WFHighLevelOpVersionFilter;
  neverPeek?: boolean;
  variant?: LinkVariant;
}> = props => {
  const {peekingRouter, baseRouter} = useWeaveflowRouteContext();
  const router = props.neverPeek ? baseRouter : peekingRouter;
  return (
    <Link
      $variant={props.variant}
      to={router.opVersionsUIUrl(props.entity, props.project, props.filter)}>
      {props.versionCount} version{props.versionCount !== 1 ? 's' : ''}
    </Link>
  );
};

export const TypeVersionsLink: React.FC<{
  entity: string;
  project: string;
  versionCount: number;
  filter?: WFHighLevelTypeVersionFilter;
}> = props => {
  const {peekingRouter} = useWeaveflowRouteContext();
  return (
    <Link
      to={peekingRouter.typeVersionsUIUrl(
        props.entity,
        props.project,
        props.filter
      )}>
      {props.versionCount} version{props.versionCount !== 1 ? 's' : ''}
    </Link>
  );
};
