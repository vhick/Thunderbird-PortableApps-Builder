// Deterministic r7 TraceGuard tests, confined to a temporary test directory.
// No real APPDATA, LOCALAPPDATA, PROGRAMDATA or live Thunderbird data is accessed.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include "../launcher/TraceGuard.h"
namespace fs=std::filesystem;
static void require(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
static void put(const fs::path& p,const char* value){fs::create_directories(p.parent_path());std::ofstream f(p);f<<value;}
int wmain(int argc,wchar_t** argv){
    try {
        require(argc==2,"Provide an isolated temporary directory");
        fs::path root=argv[1];
        fs::path portable=root/L"PortableApp"/L"Data";
        traceguard::Roots locations{root/L"Roaming",root/L"Local",root/L"ProgramData",root/L"LocalLow"};
        fs::create_directories(root);
        // Pre-existing host profile and Mozilla data must survive unchanged.
        put(locations.roaming/L"Thunderbird"/L"Profiles"/L"host-mail.txt","important mail");
        put(locations.local/L"Mozilla"/L"shared.txt","existing firefox state");
        {
            traceguard::Session a(portable,locations);require(a.ready(),"audit initialization failed");
            put(locations.local/L"Thunderbird"/L"Cache"/L"cache.txt","portable session cache");
            put(locations.programData/L"Mozilla"/L"updates"/L"shared-update.txt","do not touch");
            put(locations.localLow/L"Thunderbird"/L"Cache"/L"low.txt","session-local low cache");
            a.finish(true,false);
        }
        require(fs::exists(locations.roaming/L"Thunderbird"/L"Profiles"/L"host-mail.txt"),"Existing mail destroyed");
        require(fs::exists(locations.local/L"Mozilla"/L"shared.txt"),"Existing Mozilla data destroyed");
        require(fs::exists(locations.programData/L"Mozilla"/L"updates"/L"shared-update.txt"),"ProgramData modified");
        require(!fs::exists(locations.local/L"Thunderbird"),"New Thunderbird cache remnant not captured");
        require(!fs::exists(locations.localLow/L"Thunderbird"),"New LocalLow Thunderbird folder was not captured");
        bool lowFound=false;
        for(const auto& e:fs::directory_iterator(portable/L"TraceGuard"/L"captured"/L"LocalLow"/L"Thunderbird"))
            if(fs::exists(e.path()/L"Cache"/L"low.txt"))lowFound=true;
        require(lowFound,"LocalLow captured data missing");
        fs::path captures=portable/L"TraceGuard"/L"captured"/L"Local"/L"Thunderbird";
        bool found=false;
        for(const auto& e:fs::directory_iterator(captures))
            if(fs::exists(e.path()/L"Cache"/L"cache.txt"))found=true;
        require(found,"Captured portable cache data missing");
        // An existing Local Thunderbird directory must never be touched.
        put(locations.local/L"Thunderbird"/L"installed-profile.txt","user data");
        {traceguard::Session b(portable,locations);require(b.ready(),"second initialization failed");
         put(locations.local/L"Thunderbird"/L"new.txt","new data");b.finish(true,false);}
        require(fs::exists(locations.local/L"Thunderbird"/L"installed-profile.txt"),"Existing Thunderbird data moved");
        // Pre-existing LocalLow data must stay untouched as well.
        put(locations.localLow/L"Thunderbird"/L"host-mail.txt","protected host contents");
        {traceguard::Session low(portable,locations);require(low.ready(),"LocalLow protection init failed");
         put(locations.localLow/L"Thunderbird"/L"new.txt","new after snapshot");low.finish(true,false);}
        require(fs::exists(locations.localLow/L"Thunderbird"/L"host-mail.txt"),"Existing LocalLow host contents moved");
        // Newly created *empty* Mozilla parent is safe to prune; pre-existing Mozilla stays.
        {traceguard::Session empty(portable,locations);require(empty.ready(),"empty parent init failed");
         fs::create_directories(locations.roaming/L"Mozilla"); empty.finish(true,false);}
        require(!fs::exists(locations.roaming/L"Mozilla"),"New empty Mozilla parent remained");
        // If another Thunderbird instance exists, leave even newly created folders alone.
        {traceguard::Session c(portable,locations);require(c.ready(),"third initialization failed");
         put(locations.roaming/L"Mozilla"/L"shared-stuff.txt","shared");
         c.finish(true,true);}
        require(fs::exists(locations.roaming/L"Mozilla"/L"shared-stuff.txt"),"Shared data moved");
        std::cout<<"PASS: TraceGuard Roaming/Local/LocalLow dedicated capture, existing-profile protection, ProgramData exclusion and shared-path protection\n";
        return 0;
    } catch(const std::exception& e) {std::cerr<<"TraceGuard FAIL: "<<e.what()<<"\n";return 1;}
}
