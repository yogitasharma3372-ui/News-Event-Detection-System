import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, NavTab } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { NewsExplorerPage } from './pages/NewsExplorerPage';
import { EventExplorerPage } from './pages/EventExplorerPage';
import { EventDetailPage } from './pages/EventDetailPage';
import { LiveMonitorPage } from './pages/LiveMonitorPage';
import { ResearchLabPage } from './pages/ResearchLabPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { DatasetManagementPage } from './pages/DatasetManagementPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './api/client';
import { Event } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [totalArticles, setTotalArticles] = useState(0);
  const [totalEvents, setTotalEvents] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshCounts = async () => {
    setIsRefreshing(true);
    try {
      const meta = await api.getMetadata();
      setTotalArticles(meta.total_articles);
      setTotalEvents(meta.total_events);
    } catch {
      // ignore
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshCounts();
  }, [activeTab]);

  const handleOpenEvent = (event: Event) => {
    setSelectedEventId(event.id);
  };

  const handleBackToEvents = () => {
    setSelectedEventId(null);
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      <Navbar
        onRefresh={refreshCounts}
        isRefreshing={isRefreshing}
        totalArticles={totalArticles}
        totalEvents={totalEvents}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveTab(tab);
            setSelectedEventId(null); // Clear active event detail on tab switch
          }}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            {selectedEventId ? (
              <EventDetailPage
                eventId={selectedEventId}
                onBack={handleBackToEvents}
              />
            ) : (
              <>
                {activeTab === 'overview' && (
                  <OverviewPage
                    onNavigateTab={setActiveTab}
                    onOpenEvent={handleOpenEvent}
                  />
                )}
                {activeTab === 'news-explorer' && <NewsExplorerPage />}
                {activeTab === 'event-explorer' && (
                  <EventExplorerPage onOpenEvent={handleOpenEvent} />
                )}
                {activeTab === 'live-monitor' && <LiveMonitorPage />}
                {activeTab === 'research-lab' && <ResearchLabPage />}
                {activeTab === 'evaluation' && <EvaluationPage />}
                {activeTab === 'dataset-mgmt' && <DatasetManagementPage />}
                {activeTab === 'settings' && <SettingsPage />}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
