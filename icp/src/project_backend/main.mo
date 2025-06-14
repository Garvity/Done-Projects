import Debug "mo:base/Debug";

actor {
  var currentCanisterId : Text = "";

  public func setCanisterId(id : Text) : async Text {
    if (id.size() > 0 and id.size() <= 64) {
      currentCanisterId := id;
      Debug.print("Set Canister ID: " # id);
      return "Canister ID set successfully.";
    } else {
      return "Invalid Canister ID.";
    }
  };

  public query func getCanisterId() : async Text {
    return currentCanisterId;
  };
}
