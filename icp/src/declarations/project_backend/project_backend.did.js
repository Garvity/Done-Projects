export const idlFactory = ({ IDL }) => {
  return IDL.Service({
    'getCanisterId' : IDL.Func([], [IDL.Text], ['query']),
    'setCanisterId' : IDL.Func([IDL.Text], [IDL.Text], []),
  });
};
export const init = ({ IDL }) => { return []; };
